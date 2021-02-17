import json
import os
import sys
import webbrowser
import markdown

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
  <script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
  <!-- <script src="https://cdn.jsdelivr.net/npm/vue"></script> -->
  <link rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css" />
  <style>
    [v-cloak] {
      display: none;
    }
  </style>
</head>

<body style="margin: 2rem;">
  <div style=" margin: auto" id="app" class="markdown-body">
    <h1 style="margin: 0 2rem;">原神抽卡记录导出工具 抽卡报告</h1>
    <!-- <span v-cloak>{{ message }}</span> -->
    <div>
      <div style="display: inline-block;margin: 0 2rem;" v-cloak v-for="banner in gachaType">
        <h2> {{banner.name}} </h2>
        <table>
          <thead>
            <tr>
              <th>星级</th>
              <th>数量</th>
              <th>基础概率</th>
              <th>综合概率</th>
              <th>距上次保底</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="cursor:help" v-bind:title="detail[banner.key].rank5logs">5星</td>
              <td style="cursor:help" v-bind:title="detail[banner.key].items5str">{{detail[banner.key]["5"]}}</td>
              <td>{{percent(detail[banner.key]["5"], detail[banner.key].total)}}</td>
              <td>{{percent(detail[banner.key]["5"], detail[banner.key].totalForRank5)}}</td>
              <td>{{detail[banner.key].guarantee5}}</td>
            </tr>
            <tr>
              <td>4星</td>
              <td style="cursor:help" v-bind:title="detail[banner.key].items4str">{{detail[banner.key]["4"]}}</td>
              <td>{{percent(detail[banner.key]["4"], detail[banner.key].total)}}</td>
              <td>{{percent(detail[banner.key]["4"], detail[banner.key].totalForRank4)}}</td>
              <td>{{detail[banner.key].guarantee4}}</td>
            </tr>
            <tr>
              <td>3星</td>
              <td style="cursor:help" v-bind:title="detail[banner.key].items3str">{{detail[banner.key]["3"]}}</td>
              <td>{{percent(detail[banner.key]["3"], detail[banner.key].total)}}</td>
              <td>&nbsp;</td>
              <td>&nbsp;</td>
            </tr>
            <tr>
              <td>总计</td>
              <td style="cursor:help" v-bind:title="detail[banner.key].itemsstr">{{detail[banner.key].total}}</td>
              <td>&nbsp;</td>
              <td>&nbsp;</td>
              <td>&nbsp;</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
  <script>
    gachaData = """+json.dumps(j)+"""
    for (key in gachaData.gachaLog) {
      gachaData.gachaLog[key].reverse()
    }
    function compare(p) {
      return function (m, n) {
        var a = m[p];
        var b = n[p];
        // return a - b;
        return b - a;
      }
    }
    gachaData.gachaType.sort(compare("key"));

    // for (key in gachaData.gachaLog) {
    //   if (key=="100"){
    //     delete gachaData.gachaLog["100"]
    //   }
    // }
    // tempGachaType=[]
    // for (var i in gachaData.gachaType) {
    //   var banner =gachaData.gachaType[i]
    //   console.log(banner)
    //   if (banner.key=="100"){
    //     // delete gachaData.gachaType[i]
    //   }else{
    //     tempGachaType.push(banner)
    //   }
    // }
    // gachaData.gachaType=tempGachaType;

    var app = new Vue({
      el: '#app',
      data: {
        // message: '基础概率（数量/总抽数），综合概率（数量/距上次保底已抽数）',
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
        "rank5logs": "",
      }

      for (var gacha in banner) {
        rank_type = banner[gacha]["rank_type"]
        name = banner[gacha]["name"]
        pdx = banner[gacha]["pdx"]
        if (rank_type == 5) {
          // console.log(pdx);
          detail[key]["items5"][name] = 0;
          detail[key]["rank5logs"] += " [" + name + "@" + pdx + "] ";
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

