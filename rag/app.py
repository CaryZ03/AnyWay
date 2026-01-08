from app import create_app

app = create_app()

if __name__ == '__main__':
    # ❌ 不要启用 debug（会启动 2 个进程）
    # ❌ 不要开启 reloader（debug=True 时自动开启）

    app.run(
        debug=False,            # ← 关闭 debug
        use_reloader=False,     # ← 禁用自动重载，否则会双进程
        host='0.0.0.0',
        port=5000
    )
