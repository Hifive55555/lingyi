using System;
using System.Drawing;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

/// 无边框窗口：客户区四周留了 BAND 宽的边，鼠标落在边上时返回 HTLEFT/HTBOTTOM…
/// 就能用系统原生的拖拽缩放（和无边框窗口唯一能做到“跟普通窗口一样”的办法）。
class OverlayForm : Form
{
    protected override void WndProc(ref Message m)
    {
        base.WndProc(ref m);
        if (m.Msg == OverlayHost.WM_NCHITTEST)
        {
            long lp = m.LParam.ToInt64();
            int ht = OverlayHost.BorderHit(ClientSize,
                new Point((short)(lp & 0xFFFF), (short)((lp >> 16) & 0xFFFF)), false);
            if (ht != OverlayHost.HTCLIENT) m.Result = (IntPtr)ht;
        }
    }
}

/// 标题栏：自己也要能缩放（窗口最上面那条边在它身上），否则顶部拖不动。
class BarPanel : Panel
{
    protected override void WndProc(ref Message m)
    {
        base.WndProc(ref m);
        if (m.Msg == OverlayHost.WM_NCHITTEST)
        {
            long lp = m.LParam.ToInt64();
            int ht = OverlayHost.BorderHit(ClientSize,
                new Point((short)(lp & 0xFFFF), (short)((lp >> 16) & 0xFFFF)), true);
            if (ht != OverlayHost.HTCLIENT) m.Result = (IntPtr)ht;
        }
    }
}

class OverlayHost
{
    static string ErrLog = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "wv2_err.log");
    static void Log(string s)
    {
        try { File.AppendAllText(ErrLog, DateTime.Now.ToString("HH:mm:ss ") + s + "\r\n"); } catch { }
    }

    [DllImport("user32.dll")] static extern bool ReleaseCapture();
    [DllImport("user32.dll")] static extern IntPtr SendMessage(IntPtr h, int msg, IntPtr w, IntPtr l);

    const int WM_NCLBUTTONDOWN = 0xA1;
    internal const int WM_NCHITTEST = 0x84;
    const int HTCAPTION = 0x2;
    const int BAND = 6;                 // 可拖拽的边框宽度（页面四周留出的手感区）

    // HT* 命中测试返回值
    internal const int HTCLIENT = 1, HTLEFT = 10, HTRIGHT = 11, HTTOP = 12, HTBOTTOM = 13,
              HTTOPLEFT = 13 + 3, HTTOPRIGHT = 14 + 3, HTBOTTOMLEFT = 16, HTBOTTOMRIGHT = 17;

    /// 根据“客户区内坐标”判断该点是不是可缩放边框，返回 HT* 或 HTCLIENT。
    internal static int BorderHit(Size client, Point p, bool topEdge)
    {
        bool left = p.X < BAND, right = p.X >= client.Width - BAND,
             bottom = p.Y >= client.Height - BAND,
             top = topEdge && p.Y < BAND;
        if (top && left) return 19;      // HTTOPLEFT
        if (top && right) return 20;     // HTTOPRIGHT
        if (bottom && left) return 16;   // HTBOTTOMLEFT
        if (bottom && right) return 17;  // HTBOTTOMRIGHT
        if (top) return HTTOP;
        if (bottom) return HTBOTTOM;
        if (left) return HTLEFT;
        if (right) return HTRIGHT;
        return HTCLIENT;
    }

    /// 尺寸记忆：同一台机器、同一个窗口标题，下次开还是上次拖的大小。
    static string SizeFile(string title)
    {
        foreach (char c in Path.GetInvalidFileNameChars()) title = title.Replace(c, '_');
        return Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "wv2_size_" + title + ".txt");
    }
    static bool LoadSize(string title, ref int w, ref int h)
    {
        try
        {
            string f = SizeFile(title);
            if (!File.Exists(f)) return false;
            string[] a = File.ReadAllText(f).Trim().Split(',');
            int ww, hh;
            if (a.Length == 2 && int.TryParse(a[0], out ww) && int.TryParse(a[1], out hh) && ww > 200 && hh > 200)
            { w = ww; h = hh; return true; }
        }
        catch { }
        return false;
    }
    static void SaveSize(string title, int w, int h)
    {
        try { File.WriteAllText(SizeFile(title), w + "," + h); } catch { }
    }
    static readonly Color Bg = Color.FromArgb(20, 24, 29);
    static readonly Color Bar = Color.FromArgb(28, 33, 40);
    static readonly Color Fg = Color.FromArgb(208, 216, 224);

    [STAThread]
    static void Main(string[] args)
    {
        string url = args.Length > 0 ? args[0] : "http://127.0.0.1:8761/";
        int w = args.Length > 1 ? int.Parse(args[1]) : 480;
        int h = args.Length > 2 ? int.Parse(args[2]) : 860;
        string udf = (args.Length > 3 && args[3].Length > 0) ? args[3] : null;
        string winTitle = (args.Length > 4 && args[4].Length > 0) ? args[4] : "灵弈小窗";
        int px = -1, py = 60;                     // 传了就这么摆，没传就贴右边
        if (args.Length > 5) int.TryParse(args[5], out px);
        if (args.Length > 6) int.TryParse(args[6], out py);

        Application.SetUnhandledExceptionMode(UnhandledExceptionMode.CatchException);
        Application.ThreadException += (s, e) => { Log("THREAD: " + e.Exception); Environment.Exit(9); };
        AppDomain.CurrentDomain.UnhandledException += (s, e) => { Log("DOMAIN: " + e.ExceptionObject); };

        Application.EnableVisualStyles();
        var f = new OverlayForm();
        f.Text = winTitle;
        f.FormBorderStyle = FormBorderStyle.None;      // 自绘标题栏：这样既能拖，也不吃 Edge 的窗口样式
        f.StartPosition = FormStartPosition.Manual;
        var scr = Screen.PrimaryScreen.WorkingArea;
        LoadSize(winTitle, ref w, ref h);          // 上次拖出来的大小优先
        if (px < 0) px = scr.Right - w - 30;
        // 窗口高度 = 页面高度 + 标题栏高度：这样页面拿到的视口正好是 h，
        // 和浏览器里看到的版式一致（否则页面少 26px，底部总是缺一条）。
        f.Bounds = new Rectangle(px, py, w, h + 26);
        f.TopMost = true;
        f.BackColor = Bg;
        f.MinimumSize = new Size(320, 420);       // 拖太小页面就废了，卡个下限
        f.FormClosing += (s2, e2) => SaveSize(winTitle, f.Width, f.Height - 26);

        // 自绘标题栏：拖动条 + 标题 + 关闭按钮
        var bar = new BarPanel();
        bar.Dock = DockStyle.Top;
        bar.Height = 26;
        bar.BackColor = Bar;
        var title = new Label();
        title.Text = winTitle;
        title.AutoSize = false;
        title.Dock = DockStyle.Fill;
        title.TextAlign = ContentAlignment.MiddleLeft;
        title.Padding = new Padding(10, 0, 0, 0);
        title.ForeColor = Fg;
        title.Font = new Font("Microsoft YaHei UI", 9f);
        bar.Controls.Add(title);

        var close = new Label();
        close.Text = "✕";
        close.AutoSize = false;
        close.Width = 30;
        close.Dock = DockStyle.Right;
        close.TextAlign = ContentAlignment.MiddleCenter;
        close.ForeColor = Fg;
        close.BackColor = Bar;
        close.Font = new Font("Microsoft YaHei UI", 9.5f);
        close.Cursor = Cursors.Hand;
        close.Click += (s, e) => Application.Exit();
        bar.Controls.Add(close);

        var min = new Label();
        min.Text = "—";
        min.AutoSize = false;
        min.Width = 30;
        min.Dock = DockStyle.Right;
        min.TextAlign = ContentAlignment.MiddleCenter;
        min.ForeColor = Fg;
        min.BackColor = Bar;
        min.Font = new Font("Microsoft YaHei UI", 9.5f);
        min.Cursor = Cursors.Hand;
        min.Click += (s, e) => f.WindowState = FormWindowState.Minimized;
        bar.Controls.Add(min);

        MouseEventHandler dragStart = (s, e) =>
        {
            if (e.Button == MouseButtons.Left)
            {
                ReleaseCapture();
                SendMessage(f.Handle, WM_NCLBUTTONDOWN, (IntPtr)HTCAPTION, IntPtr.Zero);
            }
        };
        bar.MouseDown += dragStart;
        title.MouseDown += dragStart;

        // 布局：标题栏占顶部 26px，WebView2 放进一个**独立的容器面板**里再 Dock=Fill。
        //
        // 为什么不直接把 WebView2 摆到 (0,26)：WinForms 包装器是按“控件相对窗体”
        // 去算渲染区的，控件带 y 偏移时它算成了 (0,0,w,h-26) —— 页面整体上移 26px，
        // 于是标题栏盖住页面第一行、底部还少一条（实测截图就是这个现象）。
        // 套一层面板后控件在面板内是 (0,0)，渲染区和面板完全对齐。
        var wv = new WebView2();
        var host = new Panel();
        const int BAR_H = 26;
        wv.Dock = DockStyle.Fill;
        host.Controls.Add(wv);
        f.Controls.Add(host);
        f.Controls.Add(bar);
        EventHandler layout = (s2, e2) =>
        {
            int w2 = f.ClientSize.Width, h2 = f.ClientSize.Height;
            bar.SetBounds(0, 0, w2, BAR_H);
            // 左右下各留 BAND 宽的一条给窗体自己（鼠标落在上面才能拿到 WM_NCHITTEST，
            // WebView2 的子窗口会把鼠标全吃掉），这条底色 = 页面底色，看着就是一条细边。
            host.SetBounds(BAND, BAR_H, Math.Max(40, w2 - 2 * BAND), Math.Max(40, h2 - BAR_H - BAND));
        };
        f.Resize += layout;

        f.Shown += async (s, e) =>
        {
            try
            {
                Log("CreateAsync udf=" + (udf ?? "(exe 同级默认)"));
                var env = await CoreWebView2Environment.CreateAsync(null, udf, null);
                await wv.EnsureCoreWebView2Async(env);
                layout(null, EventArgs.Empty);      // core 起来后再摆一次（此时控件尺寸已定）
                wv.CoreWebView2.Settings.AreDefaultContextMenusEnabled = false;
                wv.CoreWebView2.Settings.IsStatusBarEnabled = false;
                wv.CoreWebView2.Settings.AreDevToolsEnabled = false;
                wv.CoreWebView2.NavigationCompleted += (s2, e2) =>
                    Log("nav ok=" + e2.IsSuccess + " " + e2.WebErrorStatus);
                wv.CoreWebView2.Navigate(url);
                Log("navigating " + url);
            }
            catch (Exception ex)
            {
                Log("FAIL " + ex.GetType().Name + ": " + ex.Message);
                Application.Exit();
            }
        };
        layout(null, EventArgs.Empty);
        Application.Run(f);
    }
}
