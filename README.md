# 灵动闪避 (IntelliDodge)

![Game Screenshot](https://via.placeholder.com/800x600/000000/FFFFFF/?text=IntelliDodge+Game+Screenshot)

一款基于Python和Pygame开发的智能躲避球游戏，提供手动和自动两种控制模式。

## 游戏特点

- 🤖 **智能躲避算法**：自动模式下使用预测算法避开小球
- 🎮 **双模式切换**：支持手动鼠标控制和自动AI控制
- ⏱️ **实时计时**：记录并显示生存时间
- 🎯 **简洁界面**：清晰的视觉反馈和用户界面
- 🔄 **即时重玩**：一键重新开始游戏

## 安装要求

- Python 3.6+
- Pygame 库

## 安装步骤

1. 确保已安装Python 3.6或更高版本
2. 安装Pygame库：
pip install pygame
3. 下载游戏文件：
git clone https://github.com/yourusername/IntelliDodge.git
4. 运行游戏：
cd IntelliDodge
python intellidodge.py
## 游戏控制

- **鼠标移动**：在手动模式下控制玩家角色移动
- **空格键**：切换手动/自动模式
- **R键**：游戏结束后重新开始
- **ESC键**：退出游戏

## 游戏规则

1. 控制绿色圆形玩家角色躲避红色和蓝色小球
2. 小球会从边界反弹，速度会随时间增加
3. 一旦玩家触碰到任何小球，游戏结束
4. 目标是尽可能长时间生存，创造最高生存时间记录

## 自动模式算法

游戏采用预测算法来计算小球未来位置，并评估多个候选移动方向的安全性，选择最优路径避开小球。算法考虑以下因素：
- 小球当前位置和速度向量
- 预测未来多个时间步长的位置
- 边界碰撞的预测反弹
- 与所有小球的综合安全距离

## 项目结构
IntelliDodge/
├── intellidodge.py # 主游戏文件
├── README.md # 项目说明文档
└── requirements.txt # 依赖库列表
## 开发者

由AI助手开发，基于Python和Pygame库构建。

## 许可证

本项目采用MIT许可证。详情请查看LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进游戏：
- 报告BUG
- 提出新功能建议
- 优化算法性能
- 改进用户界面

## 更新日志

### v1.0.0 (2024-08-24)
- 初始版本发布
- 实现基本游戏功能
- 添加手动和自动模式
- 实现智能躲避算法
