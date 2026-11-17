# -*- coding: utf-8 -*-
"""想定编辑智能体（Scenario Editing Agent）。

把「自然语言描述的作战场景」变成「可加载、可推演、可批量派生的灵弈想定」。

    from sce_agent import RuleParser, Builder, LuaClient
    spec = RuleParser().parse("……中文作战描述……").spec
    with LuaClient("10.42.97.205", 21001) as c:
        res = Builder(c).build(spec)
        print(res.ok, res.scen_path)
"""
__version__ = "0.1.0"

from .spec import ScenarioSpec, Side, Unit, Mission, Weather, SpecError  # noqa: F401
from .catalog import Catalog, Platform                                     # noqa: F401
from .nlu import RuleParser, ParseResult, parse                            # noqa: F401
from .lua_gen import generate, LuaProgram                                  # noqa: F401
from .builder import Builder, BuildResult                                  # noqa: F401
from .digest import parse_scenario_xml, digest_summary                     # noqa: F401
from .verify import verify, Report                                         # noqa: F401
from .lyclient import LuaClient, LuaError                                  # noqa: F401

__all__ = ["ScenarioSpec", "Side", "Unit", "Mission", "Weather", "SpecError",
           "Catalog", "Platform", "RuleParser", "ParseResult", "parse",
           "generate", "LuaProgram", "Builder", "BuildResult",
           "parse_scenario_xml", "digest_summary", "verify", "Report",
           "LuaClient", "LuaError", "__version__"]
