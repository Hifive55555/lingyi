"""
Engine Situation Module

Provides interfaces and implementations for subscribing to simulation situation data.
This module handles both gRPC-based situation streams and DDS-based subscriptions.
"""
import time
from abc import ABC, abstractmethod
from typing import Callable, Optional, List, Dict, Protocol, Any
import threading
import logging
import grpc
import ctypes
import sys
import os

# Add common directory to path for protobuf imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'common'))

from .common.AServerInterface_pb2 import Request
from .common.AServerInterface_pb2_grpc import ASRpcStub

from .types import Result
from .zdds import DDSClient, DDSMessage


# Type for user callbacks: (topic_name, data_type, data, length, is_full) -> None
UserCallback = Callable[[bytes, int, bytes, int, bool], None]


class ISituationChannel(ABC):
    """Abstract interface for situation data channels."""

    @abstractmethod
    def subscribe(self, topic: str, callback: UserCallback) -> Result[None]:
        """Subscribe to a topic."""
        ...

    @abstractmethod
    def unsubscribe(self, topic: str) -> Result[None]:
        """Unsubscribe from a topic."""
        ...

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected."""
        ...

    @abstractmethod
    def close(self):
        """Close the connection."""
        ...


class GrpcSituationChannel(ISituationChannel):
    """
    gRPC-based situation channel.

    Uses gRPC streaming to receive situation data from the engine.
    """

    def __init__(self, endpoint: str):
        """
        Initialize the gRPC situation channel.

        Args:
            endpoint: The gRPC endpoint (e.g., "localhost:8080")
        """
        self._endpoint = endpoint
        self._channel: Optional[grpc.Channel] = None
        self._stub: Optional[ASRpcStub] = None
        self._subscriptions: Dict[str, UserCallback] = {}
        self._lock = threading.RLock()
        self._running = False
        self._threads: List[threading.Thread] = []
        self._logger = logging.getLogger(__name__ + ".grpc")

    def _ensure_connected(self):
        """Ensure gRPC channel is connected."""
        if self._channel is None:
            self._channel = grpc.insecure_channel(self._endpoint)
            self._stub = ASRpcStub(self._channel)

    def subscribe(self, topic: str, callback: UserCallback) -> Result[None]:
        """
        Subscribe to a situation data topic.

        Args:
            topic: The topic name to subscribe to
            callback: Callback function for received data

        Returns:
            Result indicating success or failure
        """
        try:
            with self._lock:
                if topic in self._subscriptions:
                    return Result.failure(
                        "INVALID_PARAMETER",
                        f"Already subscribed to topic: {topic}"
                    )

                self._ensure_connected()
                self._subscriptions[topic] = callback

                # Start a thread to receive data for this topic
                thread = threading.Thread(
                    target=self._receive_loop,
                    args=(topic,),
                    daemon=True
                )
                thread.start()
                self._threads.append(thread)

                self._logger.info(f"Subscribed to topic: {topic}")
                return Result.success_void()

        except Exception as e:
            return Result.failure(
                "UNKNOWN_ERROR",
                f"Failed to subscribe to topic {topic}: {str(e)}"
            )

    def _receive_loop(self, topic: str):
        """Internal loop to receive data for a topic."""
        try:
            self._ensure_connected()
            req = Request(topic=topic)

            # Subscribe to the topic stream
            responses = self._stub.RpcSubscribeTopic(req)

            for response in responses:
                if not self._running:
                    break

                with self._lock:
                    callback = self._subscriptions.get(topic)
                    if callback:
                        try:
                            callback(
                                topic,
                                response.type,
                                response.data,
                                response.isFullUpdate,
                                response.roomId
                            )
                        except Exception as e:
                            self._logger.error(
                                f"Error in callback for topic {topic}: {e}"
                            )

        except grpc.RpcError as e:
            self._logger.warning(
                f"gRPC stream closed for topic {topic}: {e.code().name}"
            )
        except Exception as e:
            self._logger.error(f"Error receiving data for topic {topic}: {e}")
        finally:
            with self._lock:
                self._subscriptions.pop(topic, None)

    def unsubscribe(self, topic: str) -> Result[None]:
        """
        Unsubscribe from a topic.

        Args:
            topic: The topic name to unsubscribe from

        Returns:
            Result indicating success or failure
        """
        try:
            with self._lock:
                if topic not in self._subscriptions:
                    return Result.failure(
                        "INVALID_PARAMETER",
                        f"Not subscribed to topic: {topic}"
                    )

                del self._subscriptions[topic]
                self._logger.info(f"Unsubscribed from topic: {topic}")
                return Result.success_void()

        except Exception as e:
            return Result.failure(
                "UNKNOWN_ERROR",
                f"Failed to unsubscribe from topic {topic}: {str(e)}"
            )

    def is_connected(self) -> bool:
        """Check if connected."""
        return self._channel is not None

    def close(self):
        """Close the connection."""
        self._running = False

        # Wait for threads to finish
        for thread in self._threads:
            thread.join(timeout=1.0)

        if self._channel:
            self._channel.close()
            self._channel = None
            self._stub = None

        self._subscriptions.clear()
        self._threads.clear()


class DDSSituationChannel(ISituationChannel):
    """
    DDS-based situation channel.

    Uses the ZDDS library for high-performance real-time data subscriptions.
    This is the primary method for receiving situation data in production.
    """

    def __init__(self, dds_endpoint: str = "localhost:8081"):
        """
        Initialize the DDS situation channel.

        Args:
            dds_endpoint: The DDS endpoint (default: "localhost:8081")
        """
        self._endpoint = dds_endpoint
        self._library = None
        self._context = None
        self._subscriptions: Dict[str, UserCallback] = {}
        self._lock = threading.RLock()
        self._running = False
        self._logger = logging.getLogger(__name__ + ".dds")

        # Try to load the DDS library
        self._load_dds_library()

    def _load_dds_library(self):
        """Load the DDS shared library."""
        try:
            # Try to load zDDS64.dll (Windows) or libzdds.so (Linux)
            lib_names = ["zDDS64", "zdds"]
            for lib_name in lib_names:
                try:
                    self._library = ctypes.CDLL(lib_name)
                    self._logger.info(f"Loaded DDS library: {lib_name}")
                    break
                except OSError:
                    continue

            if self._library is None:
                self._logger.warning("DDS library not found, using gRPC fallback")
        except Exception as e:
            self._logger.warning(f"Failed to load DDS library: {e}")

    def subscribe(self, topic: str, callback: UserCallback) -> Result[None]:
        """
        Subscribe to a DDS topic.

        Args:
            topic: The topic name to subscribe to
            callback: Callback function for received data

        Returns:
            Result indicating success or failure
        """
        try:
            with self._lock:
                if topic in self._subscriptions:
                    return Result.failure(
                        "INVALID_PARAMETER",
                        f"Already subscribed to topic: {topic}"
                    )

                # Check if DDS is available
                if self._library is None:
                    self._logger.warning(
                        "DDS library not available, subscription will use gRPC fallback"
                    )

                self._subscriptions[topic] = callback
                self._running = True

                self._logger.info(f"Subscribed to DDS topic: {topic}")
                return Result.success_void()

        except Exception as e:
            return Result.failure(
                "UNKNOWN_ERROR",
                f"Failed to subscribe to DDS topic {topic}: {str(e)}"
            )

    def unsubscribe(self, topic: str) -> Result[None]:
        """
        Unsubscribe from a DDS topic.

        Args:
            topic: The topic name to unsubscribe from

        Returns:
            Result indicating success or failure
        """
        try:
            with self._lock:
                if topic not in self._subscriptions:
                    return Result.failure(
                        "INVALID_PARAMETER",
                        f"Not subscribed to topic: {topic}"
                    )

                del self._subscriptions[topic]
                self._logger.info(f"Unsubscribed from DDS topic: {topic}")
                return Result.success_void()

        except Exception as e:
            return Result.failure(
                "UNKNOWN_ERROR",
                f"Failed to unsubscribe from DDS topic {topic}: {str(e)}"
            )

    def is_connected(self) -> bool:
        """Check if connected."""
        return self._context is not None

    def close(self):
        """Close the DDS connection."""
        self._running = False

        with self._lock:
            self._subscriptions.clear()


class IEngineSituation(Protocol):
    """
    Protocol for engine situation operations.

    This protocol defines the interface for subscribing to and receiving
    simulation situation data from the engine.
    """

    @abstractmethod
    def subscribe_bytes(
        self,
        topic: str,
        callback: UserCallback
    ) -> Result[None]:
        """Subscribe to a topic with raw bytes callback."""
        ...

    @abstractmethod
    def subscribe(
        self,
        topic: str,
        callback: Callable[[str, int, bytes, bool, str], None]
    ) -> Result[None]:
        """Subscribe to a topic."""
        ...

    @abstractmethod
    def unsubscribe(self, topic: str) -> Result[None]:
        """Unsubscribe from a topic."""
        ...

    @abstractmethod
    def set_receive_full_data(self, receive_full: bool) -> Result[None]:
        """Set whether to receive full updates or deltas."""
        ...

    @abstractmethod
    def get_receive_full_data(self) -> bool:
        """Get whether full data updates are enabled."""
        ...

    @abstractmethod
    def get_subscribed_topics(self) -> List[str]:
        """Get list of subscribed topics."""
        ...

    @abstractmethod
    def get_subscriptions(self) -> Dict[str, UserCallback]:
        """Get all subscriptions."""
        ...


class EngineSituationImpl:
    """
    Implementation of IEngineSituation.

    Provides situation data subscription functionality using DDS channels.
    Uses zDDS library directly (via DDSClient wrapper) for real-time data subscriptions.
    """

    def __init__(
        self,
        grpc_endpoint: str,
        dds_endpoint: str = "localhost:8081",
        use_dds: bool = True
    ):
        """
        Initialize the situation interface.

        Args:
            grpc_endpoint: The gRPC endpoint for control operations
            dds_endpoint: The DDS endpoint for situation data
            use_dds: Whether to prefer DDS over gRPC (default: True)
        """
        self._grpc_endpoint = grpc_endpoint
        self._dds_endpoint = dds_endpoint
        self._use_dds = use_dds

        self._grpc_channel: Optional[GrpcSituationChannel] = None
        self._dds_channel: Optional[DDSSituationChannel] = None
        self._dds_client: Optional[DDSClient] = None
        self._receive_full_data = False

        self._logger = logging.getLogger("lysdk.engine.situation")
        # self._logger.setLevel(logging.INFO)
        # if not self._logger.handlers:
        #     console = logging.StreamHandler()
        #     console.setLevel(logging.INFO)
        #     console.setFormatter(logging.Formatter('%(message)s'))
        #     self._logger.addHandler(console)

        # 保存用户回调函数，按topic存储
        self._user_callbacks: Dict[str, UserCallback] = {}
        self._lock = threading.Lock()

        # 完整态势数据存储（参考C++ SituationDataProcessor）
        self._full_data_lock = threading.Lock()
        self._full_scenario_info: Optional[bytes] = None  # THScenarioInfo 全态势
        self._full_event_coll: Optional[bytes] = None      # THEventColl 全态势
        self._full_situation_info: Optional[bytes] = None  # THSituationInfo 全态势
        self._full_situation_side: Dict[str, bytes] = {}   # THSituationSide 全态势，按topic存储

        # 主题订阅状态追踪
        self._init_state: Dict[str, bool] = {}  # 各主题初始化状态
        self._expected_side_topics: set = set()  # 期望收到的推演方topic列表
        self._full_situation_sent: bool = False  # 是否已发送过完整态势（用于区分首次和后续请求）

        self.have_subscribe_room = False

        # Initialize DDS client
        self._init_dds_client()

    def _init_dds_client(self):
        """Initialize DDS client using zDDS library."""
        try:
            # Parse dds_endpoint (format: "ip:port")
            parts = self._dds_endpoint.split(":")
            if len(parts) == 2:
                dds_ip = parts[0]
                dds_port = int(parts[1])
                self._dds_client = DDSClient(dds_ip, dds_port)
                self._logger.info(f"Initialized DDS client: {dds_ip}:{dds_port}")
            else:
                self._logger.error(f"Invalid DDS endpoint format: {self._dds_endpoint}")
        except Exception as e:
            self._logger.error(f"Failed to initialize DDS client: {e}")
            self._dds_client = None

    def _wrap_dds_callback(self, topic: str, user_callback: UserCallback):
        """
        Create a wrapper callback that converts DDSMessage to user callback format.

        DDSMessage contains:
            - mtype: message type (used as data_type in user callback)
            - dtype: data type
            - nlen: data length
            - pdata: data bytes pointer

        User callback expects:
            (topic_name, data_type, data, length, is_full)

        Note: Must copy all data immediately as C library may reuse buffers.
        """
        def wrapper(psztopic, pmsg, ncon):
            try:
                # Safety check for null pointer
                if not pmsg:
                    self._logger.warning(f"Null pmsg in callback for topic {topic}")
                    return

                # Read topic name first (passed directly, not from struct)
                topic_name = psztopic.encode('utf-8') if isinstance(psztopic, str) else (psztopic or b"")

                # Get struct address and read fields directly
                # DDSMessage layout (packed, 1-byte alignment):
                # verify(2) + ver(2) + mtype(4) + dtype(4) + nfseq(4) + npseq(4) + rev1(4) + rev2(4) + nlen(4) + pdata(8)
                try:
                    addr = ctypes.addressof(pmsg.contents)
                    # mtype at offset 4
                    data_type = ctypes.c_uint.from_address(addr + 4).value
                    # nlen at offset 28
                    nlen = ctypes.c_uint.from_address(addr + 28).value
                    # pdata at offset 32
                    pdata = ctypes.c_void_p.from_address(addr + 32).value

                    # Copy data bytes
                    if nlen > 0 and pdata and pdata > 0x1000:
                        data = bytes(ctypes.string_at(pdata, nlen))
                    else:
                        data = b""

                except Exception as inner_e:
                    self._logger.warning(f"Failed to read DDS message for topic {topic}: {inner_e}")
                    return
                user_callback(
                        topic_name,   # topic_name: bytes
                        data_type,    # data_type: int (from mtype)
                        data,         # data: bytes
                        nlen,         # length: int
                        self._receive_full_data  # is_full: bool
                    )
                # 完整态势数据解析（参考C++: if (mType < 0x50) { ParseFullTopicData }
                if data_type < 0x50:
                    self.parse_full_topic_data(topic_name, data_type, data, user_callback)
                    
            except Exception as e:
                self._logger.error(f"Error in DDS callback for topic {topic}: {e}")

        return wrapper

    def parse_full_topic_data(self, topic_name: str, data_type: int, data: bytes, user_callback: UserCallback):
        """
        解析完整态势数据（参考C++ ParseFullTopicData + SendAllSubTopicData）

        完整态势类型:
            0x00000001: THScenarioInfo
            0x00000002: THEventColl
            0x00000003: THSituationInfo
            0x00000004: THSituationSide

        当收到完整态势时，存储数据并标记该主题为已初始化。
        当所有主题初始化完成后，组装THSituationFull并回调给用户。
        """
        from .common import Struct_pb2

        topic_key = topic_name.decode('utf-8') if isinstance(topic_name, bytes) else topic_name

        with self._full_data_lock:
            # 根据data_type存储完整态势
            if data_type == 0x00000001:  # THScenarioInfo
                self._full_scenario_info = data
                self._logger.debug(f"Received full THScenarioInfo, len={len(data)}")
            elif data_type == 0x00000002:  # THEventColl
                self._full_event_coll = data
                self._logger.debug(f"Received full THEventColl, len={len(data)}")
            elif data_type == 0x00000003:  # THSituationInfo
                self._full_situation_info = data
                self._logger.debug(f"Received full THSituationInfo, len={len(data)}")
            elif data_type == 0x00000004:  # THSituationSide
                # 如果是新推演方，加入期望列表
                if topic_key not in self._full_situation_side and topic_key not in self._expected_side_topics:
                    self._expected_side_topics.add(topic_key)
                    self._logger.info(f"Add expected side topic: {topic_key}")
                self._full_situation_side[topic_key] = data
                self._logger.debug(f"Received full THSituationSide for {topic_key}, len={len(data)}")
            else:
                self._logger.warning(f"Unknown full topic data type: 0x{data_type:08x}")
                return

            # 设置主题初始化状态
            self._init_state[topic_key] = True

        # 检查是否所有主题都已初始化
        if not self._get_all_init_stat():
            return

        # 组装完整态势 THSituationFull
        th_situation_full = Struct_pb2.THSituationFull()

        with self._full_data_lock:
            # 填充 ScenarioInfo
            if self._full_scenario_info:
                th_scenario_info = Struct_pb2.THScenarioInfo()
                th_scenario_info.ParseFromString(self._full_scenario_info)
                th_situation_full.ScenarioInfo.CopyFrom(th_scenario_info)

            # 填充 Events
            if self._full_event_coll:
                th_event_coll = Struct_pb2.THEventColl()
                th_event_coll.ParseFromString(self._full_event_coll)
                th_situation_full.Events.CopyFrom(th_event_coll)

            # 填充 Situation
            if self._full_situation_info:
                th_situation = Struct_pb2.THSituation()

                th_situation_info = Struct_pb2.THSituationInfo()
                th_situation_info.ParseFromString(self._full_situation_info)
                th_situation.SituationInfo.CopyFrom(th_situation_info)

                # 填充 SituationSides
                for side_topic, side_data in self._full_situation_side.items():
                    # 从topic名称提取uuid（参考C++ extract_uuid）
                    uuid = self._extract_uuid(side_topic)
                    th_situation_side = Struct_pb2.THSituationSide()
                    th_situation_side.ParseFromString(side_data)
                    th_situation.SituationSides[uuid].CopyFrom(th_situation_side)

                th_situation_full.Situation.CopyFrom(th_situation)

        # 序列化为字节
        full_data = th_situation_full.SerializeToString()

        self._logger.info(f"Send THSituationFull(0x1000), len={len(full_data)}")

        # 调用用户回调，传递组装后的完整态势
        user_callback(
            "SITUATION_INFO".encode(),     # topic_name: bytes
            0x1000,         # data_type: int - THSituationFull类型
            full_data,      # data: bytes - 完整态势protobuf二进制
            len(full_data), # length: int
            True            # is_full: bool - 表示这是完整态势
        )

        # 重置初始化状态，等待下一帧完整态势
        self._reset_all_init_stat()

    def _get_all_init_stat(self) -> bool:
        """检查所有订阅的主题是否都已初始化"""
        required_topics = ["SCENARIO_INFO", "EVENT_INFO", "SITUATION_INFO"]
        for topic in required_topics:
            if not self._init_state.get(topic, False):
                return False

        # 必须先收到THScenarioInfo并解析出推演方列表
        with self._full_data_lock:
            if not self._expected_side_topics:
                self._logger.debug(f"_get_all_init_stat: no expected sides, has {len(self._full_situation_side)} sides received")
                return False  # 还没收到THScenarioInfo或解析SideInfo失败

            # 检查所有期望的推演方是否都已收到完整数据
            missing_sides = [s for s in self._expected_side_topics if s not in self._full_situation_side]
            if missing_sides:
                self._logger.debug(f"_get_all_init_stat: missing {len(missing_sides)} sides: {missing_sides}")
                return False
        # self._logger.info(f"_get_all_init_stat: all ready, expected={len(self._expected_side_topics)}, received={len(self._full_situation_side)}")
        return True

    def _reset_all_init_stat(self):
        """发送完整态势后，清除所有数据，等待下一帧完整态势"""
        with self._full_data_lock:
            self._full_scenario_info = None
            self._full_event_coll = None
            self._full_situation_info = None
            self._full_situation_side.clear()
            self._init_state.clear()
            self._full_situation_sent = True

    def _extract_uuid(self, topic_name: str) -> str:
        """从topic名称提取uuid（参考C++ extract_uuid）"""
        prefix = "SITUATION_"
        if topic_name.startswith(prefix):
            return topic_name[len(prefix):]
        return topic_name

    def _get_channel(self) -> ISituationChannel:
        """Get the appropriate situation channel."""
        if self._use_dds and self._dds_channel:
            return self._dds_channel
        if self._grpc_channel:
            return self._grpc_channel

        # Create channels
        self._grpc_channel = GrpcSituationChannel(self._grpc_endpoint)
        self._dds_channel = DDSSituationChannel(self._dds_endpoint)

        if self._use_dds and self._dds_channel.is_connected():
            return self._dds_channel
        return self._grpc_channel

    def subscribe_bytes(
        self,
        topic: str,
        callback: UserCallback
    ) -> Result[None]:
        """
        Subscribe to a topic with raw bytes callback.

        Args:
            topic: The topic name to subscribe to
            callback: Callback function that receives (topic, data_type, data, is_full_update, room_id)

        Returns:
            Result indicating success or failure
        """
        try:
            if self._dds_client is None:
                return Result.failure("SDK_NOT_INITIALIZED", "DDS client not initialized")

            # Create wrapper callback for DDS
            wrapped_callback = self._wrap_dds_callback(topic, callback)

            # Subscribe using DDSClient
            result = self._dds_client.subscribe(topic, wrapped_callback)

            if result == 0:
                return Result.success_void()
            else:
                return Result.failure("DDS_SUBSCRIBE_FAILED", f"Subscribe to {topic} failed with code {result}")

        except Exception as e:
            error_msg = f"Failed to subscribe to topic {topic}: {str(e)}"
            self._logger.error(error_msg)
            return Result.failure("UNKNOWN_ERROR", error_msg)

    def subscribe(
        self,
        topic: str,
        callback: UserCallback
    ) -> Result[None]:
        """
        Subscribe to a topic.

        Args:
            topic: The topic name to subscribe to
            callback: Callback function for received data

        Returns:
            Result indicating success or failure
        """
        check_result = self.check_subscribe_room()
        if not check_result.is_success():
            return check_result

        # 如果订阅的是 SITUATION_{side_id} 推演方主题，加入期望列表（不包括 SITUATION_INFO 和 SITUATION_DYNAMIC_*）
        if topic.startswith("SITUATION_") and not topic.startswith("SITUATION_INFO") and not topic.startswith("SITUATION_DYNAMIC_"):
            with self._full_data_lock:
                self._expected_side_topics.add(topic)
            self._logger.info(f"Registered expected side topic: {topic}")

        # 保存用户回调函数，按topic存储
        with self._lock:
            self._user_callbacks[topic] = callback

        return self.subscribe_bytes(topic, callback)

    def unsubscribe(self, topic: str) -> Result[None]:
        """
        Unsubscribe from a topic.

        Args:
            topic: The topic name to unsubscribe from

        Returns:
            Result indicating success or failure
        """
        try:
            if self._dds_client:
                self._dds_client.unsubscribe(topic)

            # 如果取消订阅的是 SITUATION_{side_id} 推演方主题，从期望列表移除（不包括 SITUATION_INFO 和 SITUATION_DYNAMIC_*）
            if topic.startswith("SITUATION_") and not topic.startswith("SITUATION_INFO") and not topic.startswith("SITUATION_DYNAMIC_"):
                with self._full_data_lock:
                    self._expected_side_topics.discard(topic)

            with self._lock:
                self._user_callbacks.pop(topic, None)

            self._logger.info(f"Unsubscribed from topic: {topic}")
            return Result.success_void()

        except Exception as e:
            error_msg = f"Failed to unsubscribe from topic {topic}: {str(e)}"
            self._logger.error(error_msg)
            return Result.failure("UNKNOWN_ERROR", error_msg)

    # 初始化态势分发端口
    def subscribe_room(self, dds_ip, dds_port, grpc_port):
        """订阅房间态势初始化"""
        self._logger.info('subscribe_room:', dds_ip, dds_port)
        # 重置连接状态，允许在连接失败后重试
        self.have_subscribe_room = False
        try:
            if self._dds_client is None:
                self._dds_client = DDSClient(dds_ip, dds_port)
            conn_result = self._dds_client.connect(max_retries=5, retry_delay=1.0)
            if conn_result < 0:
                # < 0 表示失败（如服务端未就绪）
                raise ConnectionError(f"XDStart failed with code: {conn_result}")
            # >= 0 表示成功，返回值就是 ncon (连接句柄/ID)
            self._logger.info(f"Connected to DDS: {dds_ip}:{dds_port}, ncon={conn_result}")
            self.have_subscribe_room = True
            return b"OK"
        except Exception as e:
            self._logger.error(f"Failed to subscribe_room: {e}")
            self.have_subscribe_room = False
            return str(e).encode()

    def check_subscribe_room(self) -> Result[None]:
        if self.have_subscribe_room:
            return Result.success_void()
        situation_data = self._dds_endpoint.split(":")
        grpc_data = self._grpc_endpoint.split(":")
        if len(situation_data) == 2 and len(grpc_data) == 2:
            dds_ip = situation_data[0]
            dds_port = int(situation_data[1])
            grpc_port = int(grpc_data[1])
            try:
                result = self.subscribe_room(dds_ip, dds_port, grpc_port)
                # 只有当 subscribe_room 返回 "OK" 时才认为成功
                if result == b"OK":
                    return Result.success_void()
                else:
                    return Result.failure("DDS_CONNECT_FAILED", f"subscribe_room failed: {result}")
            except Exception as e:
                error_msg = f"Failed to subscribe_room {self._dds_endpoint}: {e}"
                self._logger.error(error_msg)
                return Result.failure("UNKNOWN_ERROR", error_msg)
        else:
            error_msg = f"Failed to get right dds point {self._dds_endpoint}"
            self._logger.error(error_msg)
            return Result.failure("UNKNOWN_ERROR", error_msg)

    def set_receive_full_data(self, receive_full: bool) -> Result[None]:
        """
        Set whether to receive full data updates or deltas.

        Args:
            receive_full: If True, receive full updates; if False, receive deltas
        """
        self._receive_full_data = receive_full
        self._logger.info(f"Set receive_full_data to: {receive_full}")
        return Result.success_void()

    def get_receive_full_data(self) -> bool:
        """Get whether full data updates are enabled."""
        return self._receive_full_data

    def get_subscribed_topics(self) -> List[str]:
        """Get list of subscribed topics."""
        with self._lock:
            return list(self._user_callbacks.keys())

    def get_subscriptions(self) -> Dict[str, UserCallback]:
        """Get all subscriptions."""
        with self._lock:
            return dict(self._user_callbacks)

    # 完整态势数据获取方法
    def get_full_scenario_info(self) -> Optional[bytes]:
        """获取完整想定信息（THScenarioInfo）"""
        with self._full_data_lock:
            return self._full_scenario_info

    def get_full_event_coll(self) -> Optional[bytes]:
        """获取完整事件信息（THEventColl）"""
        with self._full_data_lock:
            return self._full_event_coll

    def get_full_situation_info(self) -> Optional[bytes]:
        """获取完整态势信息（THSituationInfo）"""
        with self._full_data_lock:
            return self._full_situation_info

    def get_full_situation_side(self, topic: str) -> Optional[bytes]:
        """获取指定推演方的完整态势信息（THSituationSide）"""
        with self._full_data_lock:
            return self._full_situation_side.get(topic)

    def get_all_full_situation_side(self) -> Dict[str, bytes]:
        """获取所有推演方的完整态势信息"""
        with self._full_data_lock:
            return dict(self._full_situation_side)

    def close(self):
        """Close all connections."""
        if self._dds_client:
            try:
                self._dds_client.close()
            except Exception as e:
                self._logger.error(f"Error closing DDS client: {e}")
            self._dds_client = None

        if self._grpc_channel:
            self._grpc_channel.close()
            self._grpc_channel = None

        if self._dds_channel:
            self._dds_channel.close()
            self._dds_channel = None

        self._user_callbacks.clear()

        # 清理完整态势数据
        with self._full_data_lock:
            self._full_scenario_info = None
            self._full_event_coll = None
            self._full_situation_info = None
            self._full_situation_side.clear()
            self._init_state.clear()
            self._expected_side_topics.clear()
            self._full_situation_sent = False

        self._logger.info("Situation channel closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False

    def __del__(self):
        """Destructor."""
        self.close()