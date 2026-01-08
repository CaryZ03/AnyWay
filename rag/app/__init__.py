from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    
    # 注册蓝图
    from app.routes import bp as main_bp
    from app.health import health_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(health_bp)
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app















