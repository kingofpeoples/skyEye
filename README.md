# skyEye
skyEye是一个利用《天眼查》来爬取企业的控股子公司、ICP备案信息、微信公众号、企业APP等信息的资产收集工具,支持多种可选功能

$ python skyEye.py

usage: skyEye.py [-h] [-r RATE] [-d DEEP] [-m MODE] [-s DELAY] [-t TOKEN] [-u TARGET] [-ci CHILDICP] [-cw CHILDWECHAT]
                 [-ca CHILDAPP] [-cl CHILDALL]

skyEye是一个利用《天眼查》来爬取企业的控股子公司、ICP备案信息、微信公众号、企业APP等信息的资产收集工具,某些功能需要《天眼查》
ken。后的auth_token,第一次运行程序会生成配置文件：config.yaml,可在其中配置auth_to

optional arguments:
  -h, --help            show this help message and exit
  -r RATE, --rate RATE  控股比例,默认为50 [50/90/100]
  -d DEEP, --deep DEEP  控股子公司递归查询深度,默认n级 [1/2/3/.../n]
  -m MODE, --mode MODE  指定搜索模块，默认all(多个以[,]隔开) [subCompany/icp/wechat/app]
  -s DELAY, --delay DELAY
                        请求延迟，防止被ban,默认1秒
  -t TOKEN, --token TOKEN
                        指定token,似乎有20天+的有效期,一次指定短期可用,默认空
  -u TARGET, --target TARGET
                        查询目标名称(必须指定,可简称/关键字)
  -ci CHILDICP, --childICP CHILDICP
                        是否查询控股子公司ICP备案信息,默认False
  -cw CHILDWECHAT, --childWechat CHILDWECHAT
                        是否查询控股子公司微信公众号信息,默认False
  -ca CHILDAPP, --childAPP CHILDAPP
                        是否查询控股子公司APP信息,默认False
  -cl CHILDALL, --childALL CHILDALL
                        是否查询控股子公司所有(icp、公众号、app)信息,默认False
