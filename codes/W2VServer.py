import gensim
import web

model_cn = gensim.models.KeyedVectors.load_word2vec_format('/home/bill/cdminer/ijcai/corpus_data/w2v/chineseembedding_0207_toload.txt',binary=False)        

urls = (
    '/', 'index'
)
app = web.application(urls, globals())

class index:        
    def GET(self):
			i = web.input()
			w1 = i.w1
			w2 = i.w2
			return model_cn.similarity(w1, w2)

if __name__ == "__main__":
    app.run()
