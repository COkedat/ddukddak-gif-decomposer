# 대충 GIF 이미지를 분해해서 일괄 저장하는 코드

from tqdm import tqdm
import sys
import configparser
from PIL import Image
import os
from glob import glob
from tkinter import filedialog

class GifDecomposer:
    # 생성자
    def __init__(self):
        # 설정 파일 경로 설정
        base_path = os.path.dirname(sys.argv[0])
        config_path = os.path.join(base_path, 'config.ini')

        # 설정 파일이 없다면 만듦
        if not os.path.exists(config_path):
            # 설정 파일 생성
            self.makeConfig(config_path)
        
        # 설정 파일을 불러옴
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path)
        
        # img_save 섹션
        self.use_folder = config.getboolean('img_save', 'use_folder') \
            if (config.getboolean('img_save', 'use_folder') is not None) else True
        self.save_folder = config.get('img_save', 'save_folder') \
            if (config.get('img_save', 'save_folder') is not None) else 'output'
        self.save_on_exe_folder = config.getboolean('img_save', 'save_on_exe_folder') \
            if (config.getboolean('img_save', 'save_on_exe_folder') is not None) else True
        self.save_on_exe_folder = config.getboolean('img_save', 'is_transparent') \
            if (config.getboolean('img_save', 'is_transparent') is not None) else False
        
        # img_path 섹션
        self.is_path_override = config.getboolean('img_path', 'is_path_override') \
            if (config.getboolean('img_path', 'is_path_override') is not None) else False
        self.path_override = config.get('img_path', 'path_override') \
            if (config.get('img_path', 'path_override') is not None) else 'C:\\Users\\Administrator\\Desktop'
                
    
    # 이미지 오염 여부 확인 함수
    def is_corrupted(self, img_path):
        try:
            # 이미지를 불러와서 해상도를 확인
            img = Image.open(img_path)
            img.verify()
            return False
        except:
            return True

    # 설정 파일 생성 함수
    def makeConfig(self, config_path):
        # 설정 파일 생성
        config = configparser.ConfigParser(interpolation=None)
        
        # 설정 파일에 기본값 입력
        config['img_save'] = {}
        config['img_save']['use_folder'] = 'True'
        config['img_save']['save_folder'] = 'output'
        config['img_save']['save_on_exe_folder'] = 'True'
        config['img_save']['is_transparent'] = 'False'
        config['img_path'] = {}
        config['img_path']['is_path_override'] = 'False'
        config['img_path']['path_override'] = 'C:\\Users\\Administrator\\Desktop'

        # 설정 파일 저장
        with open(config_path, 'w') as configfile:
            config.write(configfile)

    # 이미지 저장 함수
    def img_save(self, img_path: str, color: tuple):
        
        if self.is_path_override:
            save_path = self.path_override
            save_path = os.path.join(save_path, os.path.basename(img_path)[:-len(os.path.splitext(img_path)[1])])

        # save_on_exe_folder가 True일 경우
        elif self.save_on_exe_folder:
            save_path = os.path.dirname(sys.argv[0])
            # use_folder가 True일 경우 하위 폴더를 생성
            if self.use_folder:
                # 저장 폴더 생성
                save_path = os.path.join(save_path, self.save_folder)
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                # 저장 폴더와 파일명 연결 (확장자 제거)
                save_path = os.path.join(save_path, os.path.basename(img_path)[:-len(os.path.splitext(img_path)[1])])
            else:
                # 폴더와 파일명 연결 (확장자 제거)
                save_path = os.path.join(save_path, os.path.basename(img_path)[:-len(os.path.splitext(img_path)[1])])

        # save_on_exe_folder가 False일 경우 원본 이미지와 동일한 경로에 저장
        else:
            # 원본 파일 경로
            save_path = os.path.dirname(img_path)
            # use_folder가 True일 경우 하위 폴더를 생성
            if self.use_folder:
                # 저장 폴더 생성
                save_path = os.path.join(save_path, self.save_folder)
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                # 저장 폴더와 파일명 연결 (확장자 제거)
                save_path = os.path.join(save_path, os.path.basename(img_path)[:-len(os.path.splitext(img_path)[1])])
            else:
                # 폴더와 파일명 연결 (확장자 제거)
                save_path = os.path.join(save_path, os.path.basename(img_path)[:-len(os.path.splitext(img_path)[1])])

        # 확장자만 제거 '.gif'
        imgName = img_path[:-4] 
        with Image.open(img_path) as im:
            # 씬 개수 확인
            print('\n')
            print(f'Frame Count: {im.n_frames}')
            for i in tqdm(range(im.n_frames)):
                # 해당 이미지 위치로 이동
                im.seek(i)       

                # RBGA로 변환  
                image = im.convert("RGBA")
                new_data = []            

                # 새 이미지에에 투명색을 제거하면서 복사
                for item in image.getdata():
                    # 투명색이라면
                    if item[3] == 0:
                        # 그대로 넣기
                        if self.is_transparent:
                            new_data.append(tuple(item))

                        # 지정 색으로 변경
                        else:
                            new_data.append(color)
                    # 투명 아니면
                    else:
                        # 그대로 넣기
                        if self.is_transparent:
                            new_data.append(tuple(item))
                        
                        # 알파 제거
                        else:
                            new_data.append(tuple(item[:3]))

                # RGBA 빈 이미지 생성
                if self.is_transparent:
                    new_img = Image.new("RGBA", im.size) 
                # RGB 빈 이미지 생성    
                else:
                    new_img = Image.new("RGB", im.size)   
                
                # newImage에 newData 추가
                new_img.putdata(new_data)

                # 파일로 저장
                new_img.save('{}_{}.png'.format(save_path,i))

        

def main():
    # 클래스 생성
    decomposer = GifDecomposer()

    # 이미지 파일 경로를 입력하지 않았을 경우 사용법 출력
    if len(sys.argv) < 2:
        # 기초 경로 설정
        base_path = os.path.dirname(sys.argv[0])

        print("[Mode] Image File Selection")
        img_list = filedialog.askopenfilenames(initialdir=base_path, title="Select Image Files", filetypes=[("Image Files", "*.jpg;*.png;*.jpeg;*.bmp;*.gif;*.webp")])

        # 이미지 파일이 없거나 선택하지 않았을 경우
        if (img_list is None or len(img_list) == 0):
            print("[Warning] No image files or No folder selected. Exiting...")
            input("Press Any Key to exit...")
            return
    else:
        # 인수들을 이미지 파일 리스트로 저장
        img_list = sys.argv[1:]

    # 이미지 리스트 리사이징 후 저장
    for img_o in tqdm(img_list):
        if (decomposer.is_corrupted(img_o) or img_o[-3:] != 'gif'):
            # 파일명만 출력
            print(f"[Warning] {os.path.basename(img_o)} is corrupted or NOT gif. Skipping...")
            continue
        decomposer.img_save(img_o, (255, 255, 255))
    return
    

if __name__ == '__main__':
    main()