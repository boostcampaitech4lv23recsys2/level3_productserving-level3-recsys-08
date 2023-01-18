import cmd #cmd는 별도의 설치 필요없음!
import pickle
import os
import pandas as pd

ml_title = pd.read_csv("/opt/ml/input/fighting/CSV/ml_title.csv")
mbti_all_title = pd.read_csv("/opt/ml/input/fighting/CSV/mbti_all_title.csv")
mbti_none_title = pd.read_csv("/opt/ml/input/fighting/EDA/mbti_none_title.csv")

ml_title = ml_title.dropna(axis=0)

title_list = list(ml_title['title'])
mbti_none_title_list = list(mbti_none_title['Contents'])

start_index = 0 #300
i = start_index

if os.path.exists('real_none_title.pickle'):
    with open('real_none_title.pickle', 'rb') as f:
        real_none_title = pickle.load(f)
else:
    real_none_title = []
    
if os.path.exists('dont_know_title.pickle'):
    with open('dont_know_title.pickle', 'rb') as f:
        dont_know_title = pickle.load(f)
else:
    dont_know_title = []
    
if os.path.exists('series_title.pickle'):
    with open('series_title.pickle', 'rb') as f:
        series_title = pickle.load(f)
else:
    series_title = []


def content_based_filtering_jaccard(title_list, title):
    topn=20
    target_split_set = set(title.split())
    sim_list = []
    sim_df = pd.DataFrame(title_list, columns=['title'])
    for idx, movie in enumerate(title_list):
        title_split_set = set(movie.split())
        title_intersection = target_split_set.intersection(title_split_set)
        jac_sim = float(len(title_intersection)) / (len(target_split_set) + len(title_split_set) - len(title_intersection))
        sim_list.append(jac_sim)
    sim_df['jaccard_similarity'] = sim_list

    return sim_df.sort_values('jaccard_similarity', ascending=False).reset_index(drop=True)[:topn]

# MBTI의 i번째 타이틀, 가장 유사한 ML 타이틀 20개 중 j를 데이터프레임에 추가
def make_do_j(j):
    def do_j(self, arg):
        global i
        global title_list, mbti_none_title_list, tmp, result_df
        try:
            result_df.loc[i] = {"mbti_title":mbti_none_title_list[i], \
                                "ml_title":tmp.iloc[j].title}
        except:
            result_df = pd.DataFrame({"mbti_title":[mbti_none_title_list[i]], \
                                     "ml_title":[tmp.iloc[j].title]})
        i += 1
        show_mbti_title_and_top20(i)
    return do_j


def show_mbti_title_and_top20(i):
    global tmp
    print(f'{i}번째 mbti title : \033[1;34m{mbti_none_title_list[i]}\033[0m')

    #가장 유사한 Top20 영화 출력부분
    tmp = content_based_filtering_jaccard(title_list, mbti_none_title_list[i])
    tmp.index = range(1, 21)
    print(f'[1]\t\t  \033[1;32m{tmp.loc[1].title}\033[0m\t\t\t{tmp.loc[1].jaccard_similarity}')
    print(f'[2]\t\t  \033[1;32m{tmp.loc[2].title}\033[0m\t\t\t{tmp.loc[2].jaccard_similarity}')
    print(f'[3]\t\t  \033[1;32m{tmp.loc[3].title}\033[0m\t\t\t{tmp.loc[3].jaccard_similarity}')
    print(f'[4]\t\t  \033[1;32m{tmp.loc[4].title}\033[0m\t\t\t{tmp.loc[4].jaccard_similarity}')
    print(f'[5]\t\t  \033[1;32m{tmp.loc[5].title}\033[0m\t\t\t{tmp.loc[5].jaccard_similarity}')
    print(f'[6]\t\t  \033[1;32m{tmp.loc[6].title}\033[0m\t\t\t{tmp.loc[6].jaccard_similarity}')
    print(f'[7]\t\t  \033[1;32m{tmp.loc[7].title}\033[0m\t\t\t{tmp.loc[7].jaccard_similarity}')
    print(f'[8]\t\t  \033[1;32m{tmp.loc[8].title}\033[0m\t\t\t{tmp.loc[8].jaccard_similarity}')
    print(f'[9]\t\t  \033[1;32m{tmp.loc[9].title}\033[0m\t\t\t{tmp.loc[9].jaccard_similarity}')
    print(f'[10]\t\t  \033[1;32m{tmp.loc[10].title}\033[0m\t\t\t{tmp.loc[10].jaccard_similarity}')
    print(f'[11]\t\t  \033[1;32m{tmp.loc[11].title}\033[0m\t\t\t{tmp.loc[11].jaccard_similarity}')
    print(f'[12]\t\t  \033[1;32m{tmp.loc[12].title}\033[0m\t\t\t{tmp.loc[12].jaccard_similarity}')
    print(f'[13]\t\t  \033[1;32m{tmp.loc[13].title}\033[0m\t\t\t{tmp.loc[13].jaccard_similarity}')
    print(f'[14]\t\t  \033[1;32m{tmp.loc[14].title}\033[0m\t\t\t{tmp.loc[14].jaccard_similarity}')
    print(f'[15]\t\t  \033[1;32m{tmp.loc[15].title}\033[0m\t\t\t{tmp.loc[15].jaccard_similarity}')
    print(f'[16]\t\t  \033[1;32m{tmp.loc[16].title}\033[0m\t\t\t{tmp.loc[16].jaccard_similarity}')
    print(f'[17]\t\t  \033[1;32m{tmp.loc[17].title}\033[0m\t\t\t{tmp.loc[17].jaccard_similarity}')
    print(f'[18]\t\t  \033[1;32m{tmp.loc[18].title}\033[0m\t\t\t{tmp.loc[18].jaccard_similarity}')
    print(f'[19]\t\t  \033[1;32m{tmp.loc[19].title}\033[0m\t\t\t{tmp.loc[19].jaccard_similarity}')
    print(f'[20]\t\t  \033[1;32m{tmp.loc[20].title}\033[0m\t\t\t{tmp.loc[20].jaccard_similarity}')


class MyPrompt(cmd.Cmd):
    intro = '입력받은 title(from MBTI)과 가장 유사한 \033[1mtitle(from ML) 3개(1/2/3) 중\033[0m 고르면 알아서 데이터프레임에 담아줍니다!\n\
\033[1m비슷한 영화제목이 없는 경우엔 0를\033[0m 눌러주세요!\n\
\033[1m시작하는 방법은 start\033[0m입니다.\n\
\033[1m종료하는 방법은 quit\033[0m이며, 자동으로 데이터프레임을 저장해줍니다!'
    prompt = '(my_shell) '
    result_df = pd.DataFrame()
     
    # do_1부터 do_20 함수만들기
    for j in range(1, 21):
        do_j = make_do_j(i)
        locals()["do_"+str(j)] = do_j
           
    def do_start(self, arg):
        global i, title_list, mbti_none_title_list
        show_mbti_title_and_top20(i)         

    def do_x(self, arg):
        global i
        real_none_title.append((i,mbti_none_title_list[i]))
        i += 1
        show_mbti_title_and_top20(i)
        
    def do_d(self, arg):
        global i
        dont_know_title.append((i,mbti_none_title_list[i]))
        i += 1
        show_mbti_title_and_top20(i)
    
    def do_s(self, arg):
        global i
        series_title.append((i,mbti_none_title_list[i]))
        i += 1
        show_mbti_title_and_top20(i)
        
    def do_quit(self, arg):
        global result_df
        try:
            result_df.to_csv(f'result_{start_index}부터_{i}까지.csv')
        except: pass
        with open('real_none_title.pickle', 'wb') as f:
            pickle.dump(real_none_title, f)
        with open('dont_know_title.pickle', 'wb') as f:
            pickle.dump(dont_know_title, f)
        with open('series_title.pickle', 'wb') as f:
            pickle.dump(series_title, f)
        print(f"저장된 파일이름: result_{start_index}부터_{i}까지.csv\n")
        print("비슷한 영화제목이 없는 경우 리스트: real_none_title")
        return True
    
if __name__ == '__main__':
    MyPrompt().cmdloop()