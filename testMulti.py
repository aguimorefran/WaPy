from classifier import SentimentClassifier
from concurrent import futures
from tqdm import tqdm
from threading import Lock
import multiprocessing
from time import sleep

lista = []
lista.append("Mi hijo es un gángster sin corazón, y yo necesito un abrazo")
lista.append("¿El tren ya ha partido, queréis alquiler una bicicleta?")
lista.append("El perro es el mejor amigo del hombre")
lista.append("Los pingüinos están en el agua")
lista.append("Un rey no muere nunca, solo duerme.")
lista.append("Quiero mucho ver las diapositivas de vuestra operación de hígado pero en primer lugar necesito ir cortar mi cabeza en pedazos pequeñitos con mi peine")
lista.append("Me gustam mucho ir a correr")
lista.append("Mi amiga es muy guapa")
lista.append("NO quiero ir a estudiar porque no me gusta")
lista.append("Mis amigos se portan bien conmigo")
lista.append("Quiero ir al cine")
lista.append("Estoy enfadado con mis amigos")
lista.append("Mi padre ha hecho la comida que me gusta")
lista.append("No quiero ir al cine")
lista.append("Me gustam mucho ir a correr")
lista.append("Mi amiga es muy guapa")
lista.append("NO quiero ir a estudiar porque no me gusta")
lista.append("Mis amigos se portan bien conmigo")
lista.append("Quiero ir al cine")
lista.append("Estoy enfadado con mis amigos")
lista.append("Mi padre ha hecho la comida que me gusta")
lista.append("No quiero ir al cine")
lista.append("Me gustam mucho ir a correr")
lista.append("Mi amiga es muy guapa")
lista.append("NO quiero ir a estudiar porque no me gusta")
lista.append("Mis amigos se portan bien conmigo")
lista.append("Quiero ir al cine")
lista.append("Estoy enfadado con mis amigos")
lista.append("Mi padre ha hecho la comida que me gusta")
lista.append("No quiero ir al cine")
lista.append("Me gustam mucho ir a correr")
lista.append("Mi amiga es muy guapa")
lista.append("NO quiero ir a estudiar porque no me gusta")
lista.append("Mis amigos se portan bien conmigo")
lista.append("Quiero ir al cine")
lista.append("Estoy enfadado con mis amigos")
lista.append("Mi padre ha hecho la comida que me gusta")
lista.append("No quiero ir al cine")
lista.append("Me gustam mucho ir a correr")
lista.append("Mi amiga es muy guapa")
lista.append("NO quiero ir a estudiar porque no me gusta")
lista.append("Mis amigos se portan bien conmigo")
lista.append("Quiero ir al cine")
lista.append("Estoy enfadado con mis amigos")
lista.append("Mi padre ha hecho la comida que me gusta")
lista.append("No quiero ir al cine")
lista.append("Me gustam mucho ir a correr")
lista.append("Mi amiga es muy guapa")
lista.append("NO quiero ir a estudiar porque no me gusta")
lista.append("Mis amigos se portan bien conmigo")
lista.append("Quiero ir al cine")
lista.append("Estoy enfadado con mis amigos")
lista.append("Mi padre ha hecho la comida que me gusta")
lista.append("No quiero ir al cine")
lista.append("Me gustam mucho ir a correr")
lista.append("Mi amiga es muy guapa")
lista.append("NO quiero ir a estudiar porque no me gusta")
lista.append("Mis amigos se portan bien conmigo")
lista.append("Quiero ir al cine")
lista.append("Estoy enfadado con mis amigos")
lista.append("Mi padre ha hecho la comida que me gusta")
lista.append("No quiero ir al cine")
lista.append("Mi padre ha hecho la comida que me gusta")
lista.append("No quiero ir al cine")

def classify(msgList, results):
    cores = multiprocessing.cpu_count()
    classifiers = []
    for c in range(cores):
        classifiers.append(SentimentClassifier())
        print(str(c) + " clf initialized")
    mutex = Lock()

    #divide the list and call the thread with its mod clf
    sep = len(msgList)//cores
    pool = multiprocessing.Pool(cores)
    for c in range(cores):
        first = c*sep
        last = first+sep-1
        print("Calling " + str(c))
        p = multiprocessing.Process(target=compute, args=(c, msgList, results, mutex, first, last, classifiers[c]))
        p.start()
    
    pool.close()
    pool.join()

# receives the original list and the bounds it has to compute
# iterates from msgList[first] to msgList[last], calculates the clf, acquires mutex, and does res[i] = result
def compute(id, msgList, results, mutex, first, last, clf):
    for i in range(start=first, stop=last):
        print(str(id) + " computing " + str(i))
        result = clf.predict(msgList[i])
        mutex.acquire()
        try:
            res[i] = result
        finally:
            mutex.release()

res = []
classify(lista, res)