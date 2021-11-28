import base
from web import models


def main():
    models.PricePolicy.objects.create(category=1, title='个人标题', price=0, project_num=3, project_member=2,
                                      project_space=20,
                                      per_file_size=5)


if __name__ == '__main__':
    main()
