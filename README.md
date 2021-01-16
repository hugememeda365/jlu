吉林大学研究生自动签到python脚本
=======
	/*****2021/1/16**********/
	*.此程序用于吉林大学研究生防疫自动打卡
	*.此程序同时适用于早签到，晚打卡
	*.使用前请将你的信息填写到config.json
	*.配置文件的文件名请勿更改
	*.首次使用可能缺少相应的依赖包requests, lxml.请在cmd界面运行> pip install [缺少的依赖包]
	*.此程序支持用服务器定时运行，并将本次打卡结果以微信公众号推送运行结果，具体操作见配置文件提示
	*.此程序仅供用于学习交流，请勿它用

	由于现在打卡不需要手动输入任何信息，所以你要更改打卡信息，请先到小程序手动打卡，并更改信息，再用脚本打卡
	程序运行的过程以及结果不会在控制台显示，会保存在jlu.log文件中
	建议用脚本运行此程序，脚本内容如下(不要忘了给脚本添加执行权限)：
	
	vim jlu.sh

	#!bin/bash
	mk="/root/Desktop/jlu"
	# jlu.sh config.json都在放/root/Desktop/jlu文件目录下
	cd $mk
	# 进入/root/Desktop/jlu目录
	/usr/local/bin/python jlu.py
	# 执行python脚本

	然后用crontab定时执行jlu.sh
	crontab -e

	00 7 * * * echo 'sleep '$(shuf -i 0-59 -n 1)'; /root/Desktop/jlu/jlu.sh' | at now + $(shuf -i 0-180 -n 1) min
	# 在校生需要晚打卡就多加下面这个定时任务
	# 00 20 * * * echo 'sleep '$(shuf -i 0-59 -n 1)'; /root/Desktop/jlu/jlu.sh' | at now + $(shuf -i 0-180 -n 1) min
	
	7:00执行脚本，但会随机延迟0-180中某分钟，0-59中某秒再执行,也就是7:00-10:00某个时刻随机执行
	# 20:00执行脚本，但会随机延迟0-180中某分钟，0-59中某秒再执行，也就是20:00-23:00某个时刻随机执行


