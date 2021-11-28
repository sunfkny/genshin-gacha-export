import json
import os
import sys
import webbrowser

def main():
    gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    f = open(f"{gen_path}\\gachaData.json", "r", encoding="utf-8")
    j = json.load(f)
    f.close()

    html = """<!DOCTYPE html>
<html>

<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>原神抽卡记录导出工具 抽卡报告</title>
  <script src="https://cdn.jsdelivr.net/npm/vue@2.6.12/dist/vue.min.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css@4.0.0/github-markdown.css"/>
  <script src="./vue.js"></script>
  <link rel="stylesheet" href="./github-markdown.css"/>
  <link rel="stylesheet" href="./bootstrap.css">
  <style>
    [v-cloak] {
      display: none;
    }
  </style>
</head>

<body style="margin: 2rem;">
  <h1>原神抽卡记录导出工具 抽卡报告</h1>
  <div id="app" class="markdown-body row">
      <div class="col-md-12 col-lg-6 col-xl-6" style="border: 0 2rem;" v-cloak v-for="gacha_name,gacha_type in gachaType">
        <h2> {{gacha_name}} <a style="font-size:10px">{{detail[gacha_type].start_time}}</a></h2>
        <div class="table-responsive">
          <table style="display: inline-table; min-width: max-content;">
            <thead>
              <tr>
                <th>星级</th>
                <th>数量</th>
                <th>基础概率</th>
                <th>综合概率</th>
                <th>距上次</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>5星</td>
                <td style="cursor:help" v-bind:title="detail[gacha_type].items5str">{{detail[gacha_type]["5"]}}</td>
                <td>{{percent(detail[gacha_type]["5"], detail[gacha_type].total)}}</td>
                <td>{{percent(detail[gacha_type]["5"], detail[gacha_type].totalForRank5)}}</td>
                <td>{{detail[gacha_type].guarantee5}}</td>
              </tr>
              <tr>
                <td>4星</td>
                <td style="cursor:help" v-bind:title="detail[gacha_type].items4str">{{detail[gacha_type]["4"]}}</td>
                <td>{{percent(detail[gacha_type]["4"], detail[gacha_type].total)}}</td>
                <td>{{percent(detail[gacha_type]["4"], detail[gacha_type].totalForRank4)}}</td>
                <td>{{detail[gacha_type].guarantee4}}</td>
              </tr>
              <tr>
                <td>3星</td>
                <td style="cursor:help" v-bind:title="detail[gacha_type].items3str">{{detail[gacha_type]["3"]}}</td>
                <td>{{percent(detail[gacha_type]["3"], detail[gacha_type].total)}}</td>
                <td>&nbsp;</td>
                <td>&nbsp;</td>
              </tr>
              <tr>
                <td>总计</td>
                <td style="cursor:help" v-bind:title="detail[gacha_type].itemsstr">{{detail[gacha_type].total}}</td>
                <td>&nbsp;</td>
                <td>&nbsp;</td>
                <td>&nbsp;</td>
              </tr>
            </tbody>
          </table>
        </div>
        <span v-if="detail[gacha_type].rank5logs[0]">5星平均出货次数：{{Math.floor(detail[gacha_type].totalForRank5/detail[gacha_type]["5"]*100)/100}}<br></span>
        <span v-if="detail[gacha_type].rank5logs[0]">5星历史记录：</span>
        <span style="margin-right: .5rem;" v-for="log in detail[gacha_type].rank5logs">{{log}}</span>
      </div>
  </div>
  <script>
    gachaData = """+json.dumps(j)+"""
    for (key in gachaData.gachaLog) {
      gachaData.gachaLog[key].reverse()
    }

    var app = new Vue({
      el: '#app',
      data: {
        gachaData: gachaData,
        gachaLog: "",
        gachaType: "",
        detail: "",
      },
      methods: {
        percent: (num, total) => {
          if (total == 0) { return "0%" }
          return `${Math.round(num / total * 10000) / 100}%`
        }
      }
    });

    app.gachaData = gachaData;
    app.gachaType = gachaData.gachaType;
    app.gachaLog = gachaData.gachaLog;
    var detail = {}
    for (var key in gachaData.gachaLog) {
      var banner = gachaData.gachaLog[key]
      idx=0;
      pdx=0;
      for (var g in banner) {
        gacha = banner[g]
        idx+=1;
        pdx+=1;
        gacha["idx"]=idx
        gacha["pdx"]=pdx
        if(gacha.rank_type == 5){
          pdx=0
        }
      }
    }

    for (var key in gachaData.gachaLog) {
      var banner = gachaData.gachaLog[key]
      detail[key] = {
        "5": 0, "4": 0, "3": 0,
        "total": banner.length,
        "guarantee5": 0,
        "guarantee4": 0,
        "items5": {},
        "items4": {},
        "items3": {},
        "items5str": "",
        "items4str": "",
        "items3str": "",
        "items": { "w3": 0, "w4": 0, "w5": 0, "c4": 0, "c5": 0 },
        "itemsstr": "",
        "rank5logs": [],
        "start_time":""
      }

      for (var gacha in banner) {
        if (detail[key]["start_time"]==""){
          detail[key]["start_time"]=" 开始于："+banner[gacha].time
        }
        rank_type = banner[gacha]["rank_type"]
        name = banner[gacha]["name"]
        pdx = banner[gacha]["pdx"]
        if (rank_type == 5) {
          // console.log(pdx);
          detail[key]["items5"][name] = 0;
          detail[key].rank5logs.push(name + "@" + pdx);
        }
        if (rank_type == 4) {
          detail[key]["items4"][name] = 0;
        }
        if (rank_type == 3) {
          detail[key]["items3"][name] = 0;
        }
      }
      for (var gacha in banner) {
        rank_type = banner[gacha]["rank_type"]
        name = banner[gacha]["name"]
        item_type = banner[gacha]["item_type"]
        if (rank_type == 5) {
          detail[key]["items5"][name] += 1;
          detail[key]["5"] += 1;
          detail[key]["guarantee5"] = 0;
          detail[key]["guarantee4"] += 1;
          if (item_type == "武器") {
            detail[key]["items"]["w5"] += 1;
          }
          if (item_type == "角色") {
            detail[key]["items"]["c5"] += 1;
          }

        }
        if (rank_type == 4) {
          detail[key]["items4"][name] += 1;
          detail[key]["guarantee5"] += 1;
          detail[key]["guarantee4"] = 0;
          detail[key]["4"] += 1;
          if (item_type == "武器") {
            detail[key]["items"]["w4"] += 1;
          }
          if (item_type == "角色") {
            detail[key]["items"]["c4"] += 1;
          }
        }
        if (rank_type == 3) {
          detail[key]["items3"][name] += 1;
          detail[key]["guarantee5"] += 1;
          detail[key]["guarantee4"] += 1;
          detail[key]["3"] += 1;
          if (item_type == "武器") {
            detail[key]["items"]["w3"] += 1;
          }
        }
      }
      for (k in detail[key]["items5"]) {
        detail[key]["items5str"] += k + "x" + detail[key]["items5"][k] + "\\n"
      }
      for (k in detail[key]["items4"]) {
        detail[key]["items4str"] += k + "x" + detail[key]["items4"][k] + "\\n"
      }
      for (k in detail[key]["items3"]) {
        detail[key]["items3str"] += k + "x" + detail[key]["items3"][k] + "\\n"
      }
      for (k in detail[key]["items"]) {
        switch (k) {
          case "w3":
            keyName = "3星武器";
            break;
          case "w4":
            keyName = "4星武器";
            break;
          case "w5":
            keyName = "5星武器";
            break;
          case "c4":
            keyName = "4星角色";
            break;
          case "c5":
            keyName = "5星角色";
            break;
        }
        detail[key]["itemsstr"] += keyName + "x" + detail[key]["items"][k] + "\\n"
      }

      detail[key]["totalForRank5"] = detail[key].total - detail[key].guarantee5
      detail[key]["totalForRank4"] = detail[key].total - detail[key].guarantee4
      app.detail = detail
    }

  </script>
</body>

</html>"""
    
    with open(f"{gen_path}\\gachaReport.html", "w", encoding="utf-8") as f:
        f.write(html)

    webbrowser.open_new_tab('gachaReport.html')

if __name__ == "__main__":
    main()

