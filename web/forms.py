from web import models
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.conf import settings
from utils.secret import get_secret
from utils.colorwidgets.widget import ColorRadioSelect
from libs.tencent.cos import auth


class BootStrapForm:
    bootstrap_class_exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.bootstrap_class_exclude:
                continue
            old_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{old_class} form-control'
            field.widget.attrs['placeholder'] = f'请输入{field.label}'


class CodeCleanForm:
    def clean_code(self):
        code = self.cleaned_data.get('code')
        phone = self.cleaned_data.get('phone')
        redis_code = cache.get(f'{settings.PHONE_CACHE_KEY}{phone}')
        if not redis_code:
            raise ValidationError('验证码已过期')
        else:
            redis_code_string = redis_code
            if not redis_code_string == code.strip():
                raise ValidationError('验证码错误')
        return code


class RegisterForm(BootStrapForm, CodeCleanForm, forms.ModelForm):
    phone = forms.CharField(label='手机号', max_length=11, validators=[
        RegexValidator(r'^1[1|3|4|5|6|7|8|9]\d{9}$', '手机号格式错误')
    ])

    password = forms.CharField(label='密码', min_length=11, max_length=22, error_messages={
        'min_length': '密码不得低于11位',
        'max_length': '密码不得高于22位'
    }, widget=forms.PasswordInput())

    auth_password = forms.CharField(label='确认密码', widget=forms.PasswordInput())

    code = forms.CharField(label='验证码', required=True)

    class Meta:
        model = models.UserInfo
        fields = ('username', 'email', 'phone', 'password')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if models.UserInfo.objects.filter(username=username).first():
            raise ValidationError('用户名已经存在')
        else:
            return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        password = get_secret(password)
        return password

    def clean_auth_password(self):
        password = self.cleaned_data.get('password')
        auth_password = get_secret(string=self.cleaned_data.get('auth_password'))
        if not password == auth_password:
            raise ValidationError('两次密码不一致')
        return auth_password

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        exists = models.UserInfo.objects.filter(phone=phone).first()
        if exists:
            raise ValidationError('手机号已存在')
        return phone


class SmsForm(forms.Form):
    method = forms.CharField(required=True, label='请求方法')

    phone = forms.CharField(label='手机号', max_length=11, validators=[
        RegexValidator(r'^1[1|3|4|5|6|7|8|9]\d{9}$', '手机号格式错误')
    ])

    def clean_phone(self):
        method = self.cleaned_data.get('method')
        phone = self.cleaned_data.get('phone')
        exists = models.UserInfo.objects.filter(phone=phone).first()
        if method.strip() == 'register':
            if exists:
                raise ValidationError('手机号已存在')
            return phone
        elif method.strip() == 'login':
            if not exists:
                raise ValidationError('手机号不存在')
            return phone


class LoginForm(BootStrapForm, CodeCleanForm, forms.Form):
    phone = forms.CharField(label='手机号', max_length=11, validators=[
        RegexValidator(r'^1[1|3|4|5|6|7|8|9]\d{9}$', '手机号格式错误')
    ])

    code = forms.CharField(label='验证码', required=True)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        exists = models.UserInfo.objects.filter(phone=phone).first()
        if not exists:
            raise ValidationError('手机号不存在')
        return phone


class CodeLoginForm(BootStrapForm, forms.Form):
    username = forms.CharField(label='用户名', required=True)
    password = forms.CharField(label='密码', widget=forms.PasswordInput(), required=True)
    code = forms.CharField(label='验证码', required=True)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_code(self):
        real_code = self.request.session.get('code').lower()
        user_code = self.cleaned_data.get('code').lower()
        if not real_code == user_code:
            raise ValidationError('验证码错误')
        return real_code

    def clean_username(self):
        username = self.cleaned_data.get('username')
        user_obj = models.UserInfo.objects.filter(username=username).first()
        if not user_obj:
            raise ValidationError('用户不存在')
        return username

    def clean_password(self):
        username = self.cleaned_data.get('username')
        password = get_secret(self.cleaned_data.get('password'))
        user_obj = models.UserInfo.objects.filter(username=username, password=password)
        if not user_obj:
            raise ValidationError('用户名或密码错误')
        return password


class ProjectForm(BootStrapForm, forms.ModelForm):
    bootstrap_class_exclude = ('color',)

    class Meta:
        model = models.Project
        fields = ('name', 'color', 'desc')
        # 也可以这样生成
        widgets = {
            'desc': forms.Textarea(attrs={'style': 'resize:none'}),
            'color': ColorRadioSelect(attrs={'class': 'color-radio'})
        }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_name(self):
        # 1.当前用户是否创建过项目
        name = self.cleaned_data.get('name')
        exists = models.Project.objects.filter(name=name, creator=self.request.authentication).exists()
        if exists:
            raise ValidationError('请勿重新创建项目')
        # 2.当前用户是否还有额度
        project_num = self.request.price.project_num
        current_num = self.request.authentication.project_num
        if not current_num <= project_num:
            raise ValidationError('项目数余额不足')
        return name


class WikiModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Wiki
        exclude = ('project', 'depth')

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 找到相应插件并且把字段改变
        title_list = [(None, '---------')]
        title_list.extend(models.Wiki.objects.filter(project=request.project).values_list('id', 'title'))
        self.fields['parent'].choices = title_list


class FileModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.File
        fields = ('name',)

    def __init__(self, request=None, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent = parent

    def clean_name(self):
        name = self.cleaned_data.get('name')
        query_sets = models.File.objects.filter(name=name, file_type=2, project=self.request.project)
        if self.parent:
            # 如果父目录有值
            exists = query_sets.filter(parent=self.parent).exists()
        else:
            exists = query_sets.filter(parent__isnull=True).exists()
        if exists:
            raise ValidationError('文件夹已存在')
        return name


class FileForm(forms.ModelForm):
    etag = forms.CharField(label='ETag')

    class Meta:
        model = models.File
        exclude = ('project', 'file_type', 'update_user', 'update_datetime')

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_path(self):
        return f'https://{self.cleaned_data.get("path")}'

    def clean(self):
        key = self.cleaned_data.get('key')
        etag = self.cleaned_data.get('etag')
        # 向cos校验
        if not key or not etag:
            raise ValidationError("异常数据")

        else:
            try:
                res = auth(bucket=self.request.project.bucket, key=key)
            except Exception as e:
                raise ValidationError('资源不存在')
            size = self.cleaned_data.get('size')
            if etag != res.get('ETag') or size != int(res.get('Content-Length')):
                raise ValidationError('etag或size错误')
            return self.cleaned_data


class IssuesModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Issues
        exclude = ('create_time', 'creator', 'latest_update_time', 'project')
        widgets = {
            'assign': forms.Select(attrs={'class': "selectpicker", 'data-live-search': 'true'}),
            'attention': forms.SelectMultiple(
                attrs={'class': "selectpicker", 'data-live-search': 'true', 'data-actions-box': 'true'}),
            'parent': forms.Select(attrs={'class': "selectpicker", 'data-live-search': 'true'}),
        }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 问题类型不能为空，所以没有——--------
        self.fields['issues_type'].choices = models.IssuesType.objects.filter(project=request.project).values_list(
            'id', 'title')

        # 模块可以为空，可以添加——---------
        module_choices = [('', '---------')]
        module_choices.extend(models.Module.objects.filter(project=request.project).values_list('id', 'title'))
        self.fields['module'].choices = module_choices

        # 指派和关注者只能是本项目的相关人员
        total_user_list = [(request.project.creator.id, request.project.creator.username)]
        total_user_list.extend(
            models.ProjectUser.objects.filter(project=request.project).values_list('user_id', 'user__username'))
        self.fields['attention'].choices = total_user_list
        self.fields['assign'].choices = total_user_list

        # 父问题
        parent_choices = [('', '---------')]
        parent_choices.extend(models.Issues.objects.filter(project=request.project).values_list('id', 'subject'))
        self.fields['parent'].choices = parent_choices


class InviteModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.ProjectInvite
        fields = ('period', 'count')


class UpdateUserPasswordForm(forms.Form):
    password = forms.CharField(label='旧密码', min_length=11, max_length=22, error_messages={
        'min_length': '密码不得低于11位',
        'max_length': '密码不得高于22位',
        "required": "密码不得为空"
    }, widget=forms.PasswordInput(), required=True)
    new_password = forms.CharField(label='新密码', min_length=11, max_length=22, error_messages={
        'min_length': '新密码不得低于11位',
        'max_length': '新密码不得高于22位',
        "required": "新密码不得为空"
    }, widget=forms.PasswordInput(), required=True)
