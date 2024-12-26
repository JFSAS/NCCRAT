# NCCRAT

## 简介 🚀

这是一个远程管理工具（Remote Administration Tool，简称 RAT），提供了一系列强大的功能，方便您对远程主机进行控制和管理。通过直观的 GUI 界面，您可以轻松地执行各种操作，如终端管理、文件操作、进程管理等。

## 功能特性 🛠️

- **命令行终端（Shell）**：远程执行命令，实时查看输出结果。
- **屏幕控制**：远程监控和控制目标主机的屏幕。
- **文件管理**：上传、下载和管理远程主机的文件。
- **进程管理**：查看和控制远程主机的进程信息。
- **键盘记录**：记录目标主机的键盘输入。
- **摄像头访问**：远程控制和查看目标主机的摄像头。
- 更多功能正在开发中，敬请期待！

## 文件结构 📁

以下是项目的主要文件和您需要修改的部分：

* `client.py` :客户端程序，需要实现具体的客户端处理逻辑。

* `client_gui.py` :客户端GUI。

* `main_gui.py`:GUI 主程序，需要在其中实现各功能对应的界面逻辑，将占位的弹窗消息替换为您的功能代码。

* `Terminal.py`:等功能模块：例如，`Terminal.py` 实现了终端功能。您可以参考此文件，创建并实现您自己的功能模块。

* `server.py`：服务器程序，维护了 Socket 的管理、消息收发等逻辑。通常无需修改，除非您需要更改数据传输结构。

- `protect.py`: 保护程序，现有tcp管理功能。

## 通信逻辑 🌐

1. **客户端连接管理**：在 GUI 程序中，`current_client` 以元组形式存在：
   ```python
   current_client = (client_socket, send_buffer_queue, recv_buffer_queue)
   ```
2. **功能模块通信**：在您的功能模块类中，传入 `current_client`，以便进行通信。
3. **消息收发**：通过消息队列进行收发操作。发送消息时，请在消息内容前添加功能标识符，例如 Shell 功能的标识符为 `'1'`。消息头的定义可参考 

client.py

 中的 `Command` 枚举类。

## 快速开始 🎉

### 环境依赖

- Python 3.x
- 必要的第三方库，可在 `requirements.txt` 中查看。
- 由于macOS的安全限制和一些环境问题，客户端暂时只适配了Windows，服务端和保护程序可以适配macOS和Windows。

### 运行方法

1. **克隆仓库**

   ```bash
   git clone https://github.com/your_username/your_repository.git
   ```

2. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

3. **启动服务器**

   ```bash
   python server/main_gui.py
   ```

4. **启动客户端**

   ```bash
   python client/client_gui.py
   ```

5. **启动保护程序（optional）**

   ```bash
   python protect/protect.py
   ```

## 贡献指南 🤝

欢迎贡献代码！如果您有新的功能或改进建议，请提交 Pull Request。在提交之前，请确保遵循以下指南：

- 确保代码风格一致性。
- 添加必要的文档和注释。
- 测试您的代码，确保不存在明显的错误。

## 许可证 📄

本项目采用 MIT 许可证进行许可。详情请参阅 LICENSE 文件。

## 致谢 💖

感谢所有为本项目做出贡献的开发者，以及开源社区的支持！

---

*注：本项目仅供学习和交流使用，请勿用于任何非法用途。*
