## 交易表
    ID  状  态  用户  价格  实际支付  开       始  结      束    数量（年） 订      单     号
     1  已支付    1    1      0       2020-3-14   2021-3-14      1        djajdhhehkfhfjha 
     1  已支付    1    1      0       2020-3-14   2021-3-14      1        djajdhhehkfhfjha 
     1  已支付    1    1      0       2020-3-14   2021-3-14      1        djajdhhehkfhfjha 
     1  已支付    1    1      0       2020-3-14   2021-3-14      1        djajdhhehkfhfjha 
     1  已支付    1    1      0       2020-3-14   2021-3-14      1        djajdhhehkfhfjha 
     1  已支付    1    1      0       2020-3-14   2021-3-14      1        djajdhhehkfhfjha 
## 项目表
    ID   项目名    项目描述    颜色      星标      参与人数    创建者     已使用空间
    1     bbs       bbs      #6666     true      5          1           200mb
    2     luffy     luffy    #6665     false     10         1           200mb
    3     crm       crm      #5343     false     15         3           500mb
## 参与者表
    ID      项目      用户      星标
    1       1           2       true
    2       1           1       true
    3       2           1       false

## wiki表
    ID      标题      内容      项目ID    父ID     深度
    1       test      内容      1         null     1

## file表
    ID      项目      文件/文件夹名     文件大小    父目录       类型        更新时间      更新者           key(防重名)
    1       1           周杰伦            null     null      文件夹           null        xxx              11
    2       1           小周杰伦          100kb     1          文件           null        xxx              22
## issues表
    ID      标题      内容       类型(FK)         模块(FK)          状态      优先级     指派      关注      开始时间        截止时间    模式      父问题

## 评论表
    ID      content     type        creator     time        project         parent      