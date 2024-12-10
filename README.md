免责声明（Disclaimer）

本项目中的代码仅供学习、研究和参考用途。请确保在使用本代码时遵守适用的法律法规。本作者 不对任何直接或间接使用本代码导致的后果负责，包括但不限于：

使用本代码进行非法活动；

本代码在未经授权情况下被他人使用；

因本代码产生的任何安全问题。

使用本代码表示您已同意自行承担因使用本代码带来的一切后果和责任。

特别提示：如果您将本代码用于生产环境或其他敏感场景，请务必对其进行全面的安全审查与调整。


这是一款根据burp的请求包和返回包做的scan
webScan.py 指令如下

-h  帮助信息

-u  单个url扫描

-o  获取root文件夹下的poc.指定poc -o deom.json，或全部扫描 -o  *

-r 通过读取文件作为url扫描目标，比如-r url.txt -o *

默认存在的会保存在当前目录为yes文件夹中

![image](https://github.com/user-attachments/assets/f659f30b-9968-41c6-994d-077c3393be9f)

poc_burp.py

生成poc步骤如下

将你要生成的poc存放在poc.txt

![image](https://github.com/user-attachments/assets/e4b8bc8e-49da-4f83-acd0-d4debbc65b3b)

执行poc_burp.py

![image](https://github.com/user-attachments/assets/08e54736-76c1-4b3f-8868-72a8bf60d45e)

![image](https://github.com/user-attachments/assets/0037a84d-7a24-4789-8506-7deca01938b0)

然后放入root文件夹

![image](https://github.com/user-attachments/assets/97750a5a-6b52-4a68-adca-ff6712ef46c1)

执行webScan.py -u  http://****** -o converted_poc.json

![image](https://github.com/user-attachments/assets/f4daf8aa-5153-4ef7-86e0-303e76138978)


