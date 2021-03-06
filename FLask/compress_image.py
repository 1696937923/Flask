from PIL import Image
import os


def get_size(file):
    # 获取文件大小:KB
    size = os.path.getsize(file)
    return size / 1024


def get_outfile(infile, outfile):
    if outfile:
        return outfile
    dir, suffix = os.path.splitext(infile)
    outfile = '{}-out{}'.format(dir, suffix)
    return outfile


def compress_image(infile, outfile='', mb=150, step=10, quality=80):
    """不改变图片尺寸压缩到指定大小
    :param infile: 压缩源文件
    :param outfile: 压缩文件保存地址
    :param mb: 压缩目标，KB
    :param step: 每次调整的压缩比率
    :param quality: 初始压缩比率
    :return: 压缩文件地址，压缩文件大小
    """
    o_size = get_size(infile)
    print('osize:',o_size)
    if o_size <= mb:
        return infile
    outfile = get_outfile(infile, outfile)
    im = Image.open(infile)
    im.save(outfile, quality=50)
    # print("outfile:", outfile)
    # while o_size > mb:
    #     print("time")
    #     im = Image.open(infile)
    #     im.save(outfile, quality=50)
    #     if quality - step < 10:
    #         break
    #     quality -= step
    #     o_size = get_size(outfile)
    return outfile, get_size(outfile)


if __name__ == '__main__':
    outfile, size = compress_image(r'C:\Users\Lenovo\Desktop\treehole\static\images\234.jpg')
    print("outfile:",outfile," size:",size)
