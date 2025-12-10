def inject_stealth_script(page):
    """注入指纹混淆脚本，隐藏自动化特征
    
    参考 test_band-main 项目的 _inject_fingerprint_script 实现。
    通过覆盖 navigator.webdriver 等属性，降低被检测为自动化的风险。
    """
    script = '''
    // 隐藏 webdriver 特征
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    // 模拟真实浏览器的插件列表
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });
    
    // 设置语言列表
    Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-CN', 'zh', 'en']
    });
    
    // 添加 Chrome runtime 对象
    if (!window.chrome) {
        window.chrome = {};
    }
    window.chrome.runtime = {};
    
    // 覆盖 permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications'
            ? Promise.resolve({ state: Notification.permission })
            : originalQuery(parameters)
    );
    '''
    try:
        page.evaluate(script)
        # 调试日志已关闭
        # print("[反侦查] ✓ 已注入指纹混淆脚本")
    except Exception as e:
        # 如果注入失败，继续执行（某些页面可能不支持）
        # print(f"[反侦查] ⚠ 注入脚本失败: {e}")
        pass
