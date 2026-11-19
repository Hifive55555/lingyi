using System;
using System.Drawing;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

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
    const int HTCAPTION = 0x2;
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
        var f = new Form();
        f.Text = winTitle;
        f.FormBorderStyle = FormBorderStyle.None;      // 自绘标题栏：这样既能拖，也不吃 Edge 的窗口样式
        f.StartPosition = FormStartPosition.Manual;
        var scr = Screen.PrimaryScreen.WorkingArea;
        if (px < 0) px = scr.Right - w - 30;
        // 窗口高度 = 页面高度 + 标题栏高度：这样页面拿到的视口正好是 h，
        // 和浏览器里看到的版式一致（否则页面少 26px，底部总是缺一条）。
        f.Bounds = new Rectangle(px, py, w, h + 26);
        f.TopMost = true;
        f.BackColor = Bg;

        // 自绘标题栏：拖动条 + 标题 + 关闭按钮
        var bar = new Panel();
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
            bar.SetBounds(0, 0, f.ClientSize.Width, BAR_H);
            host.SetBounds(0, BAR_H, f.ClientSize.Width, Math.Max(40, f.ClientSize.Height - BAR_H));
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
