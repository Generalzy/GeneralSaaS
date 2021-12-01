from django.db import models


# Create your models here.

class UserInfo(models.Model):
    username = models.CharField(verbose_name='用户名', max_length=32, unique=True)
    password = models.CharField(verbose_name='密码', max_length=32)
    email = models.EmailField(verbose_name='邮箱', unique=True)
    phone = models.CharField(verbose_name='手机号', unique=True, max_length=11)

    project_num = models.IntegerField(verbose_name='创建的项目数量', default=0)


class PricePolicy(models.Model):
    category_choices = (
        (1, '免费版'),
        (2, '收费版'),
        (3, '其他')
    )
    category = models.SmallIntegerField(verbose_name='收费类型', default=2, choices=category_choices)
    title = models.CharField(verbose_name='标题', max_length=32)
    price = models.PositiveIntegerField(verbose_name='价格')
    # 正整数类型
    project_num = models.PositiveIntegerField(verbose_name='项目数')
    project_member = models.PositiveIntegerField(verbose_name='项目成员数')
    project_space = models.PositiveIntegerField(verbose_name='项目空间(G)')
    per_file_size = models.PositiveIntegerField(verbose_name='单文件大小(M)', null=True)

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


class Transaction(models.Model):
    status_choice = (
        (1, '未支付'),
        (2, '已支付')
    )
    status = models.SmallIntegerField(verbose_name='交易状态', choices=status_choice)
    order = models.CharField(verbose_name='订单号', max_length=64, unique=True)
    count = models.IntegerField(verbose_name='数量(年)', help_text='0表示永久')
    price = models.IntegerField(verbose_name='实际支付价格')
    start_datetime = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_datetime = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    user = models.ForeignKey(verbose_name='用户', to='UserInfo', on_delete=models.DO_NOTHING)
    price_policy = models.ForeignKey(verbose_name='价格策略', to='PricePolicy', on_delete=models.DO_NOTHING)


class Project(models.Model):
    color_choice = (
        (1, '#56b8eb'),
        (2, '#f28033'),
        (3, '#ebc656'),
        (4, '#a2d148'),
        (5, '#20bfa4'),
        (6, '#7461c2'),
        (7, '#20bfa3')
    )

    name = models.CharField(verbose_name='项目名', max_length=32)
    color = models.SmallIntegerField(verbose_name='项目颜色', choices=color_choice, default=1)
    desc = models.CharField(verbose_name='项目描述', max_length=255, null=True, blank=True)
    use_space = models.IntegerField(verbose_name='项目已使用空间(G)', default=0)
    star = models.BooleanField(verbose_name='星标', default=False)

    join_count = models.SmallIntegerField(verbose_name='参与人数', default=1)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    bucket = models.CharField(max_length=128, verbose_name='桶')
    region = models.CharField(verbose_name='区域', max_length=32)


class ProjectUser(models.Model):
    user = models.ForeignKey(verbose_name='参与者', to='UserInfo', on_delete=models.CASCADE)
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    stat = models.BooleanField(verbose_name='星标', default=False)
    create_time = models.DateTimeField(verbose_name='加入时间', auto_now_add=True)


class Wiki(models.Model):
    title = models.CharField(verbose_name='标题', max_length=32)
    content = models.TextField(verbose_name='内容')
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    depth = models.SmallIntegerField(verbose_name='深度', default=1)
    parent = models.ForeignKey(verbose_name='父文章', to='Wiki', null=True, blank=True, on_delete=models.CASCADE,
                               related_name='children')

    def __str__(self):
        return self.title


class File(models.Model):
    file_type_choice = (
        (1, '文件'),
        (2, '文件夹')
    )
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    file_type = models.SmallIntegerField(verbose_name='文件类型', choices=file_type_choice)
    name = models.CharField(verbose_name='名称', max_length=32)
    key = models.CharField(verbose_name='文件存储在cos中的key', max_length=128, null=True, blank=True)
    size = models.IntegerField(verbose_name='文件大小', null=True, blank=True)
    path = models.CharField(verbose_name='文件路径', max_length=255, null=True, blank=True)
    parent = models.ForeignKey(verbose_name='父目录', on_delete=models.CASCADE, to='File', blank=True, null=True,
                               related_name='child')
    update_user = models.ForeignKey(verbose_name='更新者', to='UserInfo', on_delete=models.CASCADE)
    update_datetime = models.DateTimeField(verbose_name='更新时间', auto_now=True)
