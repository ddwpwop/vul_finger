# WEB指纹识别



指纹数据主要来源于有漏洞的应用系统，方便快速识别出该系统类型，快速使用对应EXP从而节约时间。



### 功能介绍

| 参数    | 说明                                                         |
| ------- | ------------------------------------------------------------ |
| -t      | 线程数，默认为6，当传入的URL过多时，建议调整为50-100或者更多，如果只有几条URL建议使用10以内。 |
| -delay | 线程延迟，默认为0。                                          |
| -f      | 选择要检测的URL文件，每条URL一行，默认为1.txt                |

### 文件介绍

| 文件名        | 说明                                                         |
| ------------- | ------------------------------------------------------------ |
| vul_finger.py | 程序主要文件                                                 |
| finger.json   | 指纹数据文件                                                 |
| getmd5.py     | 重要！远程URL MD5识别，如果你想添加MD5指纹，必须通过该程序获取MD5，否则添加到的MD5可能和程序使用的不一致导致识别识别，使用方式python3 getmd5.py -u http://1.1.1.1/test.png |

### 快速使用

1.txt内容中填上URL，每行1条，默认将结果导出为output.txt

```
python3 vul_finger.py -t 5
```



### 核心文件finger.json介绍

主要指纹数据，录入格式为每行一条，以json格式为主。

```
{"id": "SIGNDATA4USER4ESS","name": " Pkpmbs建设工程质量监督系统  POC:E:\\tools\\#外网渗透系列\\nuclei\\poc\\Pkpmbs","path":"/Standard/js/login.js"}
```

其中**id**为匹配的字符串，**name**为匹配成功后导出结果的字符串，**path**为请求的URL路径。

比如检测的URL为http://1.1.1.1，结合上述最终URL为http://1.1.1.1/Standard/js/login.js，如果URL中存在字符串SIGNDATA4USER4ESS，则代表识别成功，结果会打印到output.txt



#### MD5识别

```
{"id": {"MD5": "b7834d810e5d572a0a635ff32b994ee7"},"name": "禅道 E:\\tools\\#外网渗透系列\\nuclei\\poc\\禅道","path":"/favicon.ico"}
```

首先使用getmd5.py获取远程静态文件的MD5值，然后填上正确的MD5值后修改path路径。



### 返回header

```
{"id": {"_header": "TongWeb Server"},"name": "东方通 E:\\tools\\#外网渗透系列\\nuclei\\poc\\东方通","path":"//"}
```

部分指纹需要判断返回内容的header判断系统指纹，_header参数后的值为字符串。



## 常见问题

1.为什么同一个系统识别出来的指纹有重复的？

答：因为考虑到同一个系统指纹文件不同，所以采用多种方式识别，防止漏报。
