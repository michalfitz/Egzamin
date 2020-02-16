import arcpy
from math import sqrt, atan, acos, cos, sin, pi

arcpy.env.overwriteOutput = True
         
def azym(p,q):
    try:
        dy = q[1]-p[1]
        dx = q[0]-p[0]
        if dx == 0:
            czwartak = 0
            if dy>0:
                azymut=100
            if dy<0:
                azymut=300                
        else:
            czwartak=atan(float(abs(dy))/float(abs(dx)))
            czwartak=czwartak*200/math.pi
            if dx>0:
                if dy>0:
                    azymut = czwartak
                if dy<0:
                    azymut = 400 - czwartak
                if dy==0:
                    azymut = 0
            if dx<0:
                if dy>0:
                    azymut = 200 - czwartak
                if dy<0:
                    azymut = 200 + czwartak
                if dy==0:
                    azymut = 200
        return azymut
    except Exception, err:
        arcpy.AddError("blad azymut")
        arcpy.AddError(sys.exc_traceback.tb_lineno)
        arcpy.AddError(err.message)
    finally:
        del(dx,dy,czwartak)
        

def czyt(geometria):
    try:
        lista = []
        i = 0
        for part in geometria:
            for pnt in part:
                if pnt:
                    lista.append([pnt.X, pnt.Y])
        i += 1
        return lista
    finally:
        del(i, part, pnt, geometria, lista)


def angle(az1,az2):
    angle = az2 - az1
    return(angle)


def clear_list(lista1):
    czysc = []
    for i1 in range(len(lista1)):
        
        poprzedni = i1-1
        nastepny = i1+1
        
        if poprzedni == -1:
            poprzedni = len(lista1)-2

        if nastepny > len(lista1)-1:
            nastepny = 1
            
        angle1=abs(angle(azym(lista1[i1],lista1[poprzedni]),azym(lista1[i1],lista1[nastepny])))
        
        if (angle1>(200-tolerancja) and angle1<(200+tolerancja)):
            czysc.append(i1)

    if len(czysc) == 0:
        return(lista1)
    else:   
        czysc.reverse()
           
        for index in czysc:
            lista1.pop(index)

        if czysc[-1] == 0: lista1.append(lista1[0])

        return(lista1)


def length(a,b):
    length = sqrt((a[1]-b[1])**2+(a[0]-b[0])**2)
    return(length)

def compute_range(length_of_list,x1,x2):
    if x2 - x1 < 0:
        output_range = length_of_list - x1 - 1 + x2
    else:
        output_range = x2 - x1 - 1
    return(output_range)


def create_lista_przekatnych(lista1):
    poligon = create_arcpy_polygon(lista1)
    length1 = len(lista1)-1
    lista_przekatnych = []
    for i1 in range(len(lista1)-1):
        for i2 in range(i1+2,len(lista1)-1):
            
           
            
            if (((compute_range(length1,i1,i2) == k) and ((length1 - compute_range(length1,i1,i2)) >= k2)) or ((compute_range(length1,i2,i1) == k) and ((length1 - compute_range(length1,i2,i1)) >= k2))):

             
                
                if not create_arcpy_line([lista1[i1],lista1[i2]]).crosses(poligon):
                    lista_przekatnych.append([length(lista1[i1],lista1[i2]),i1,i2])                
        
    return(lista_przekatnych)


def search_min_przekatna(lista):
    minimum = lista
    for przekatna in lista:
        if przekatna[0] < minimum[0]:
            minimum = przekatna
            
    return(minimum)




def delete_points(lista):
    najkrotsza = search_min_przekatna(create_lista_przekatnych(lista))
    object1 = range(najkrotsza[1],najkrotsza[2]+1)+[najkrotsza[1]]
    object1_1 = [lista[index] for index in object1]
    object2 = range(najkrotsza[2],len(lista)-1)+range(0,najkrotsza[1]+1)+[najkrotsza[2]]
    object2_2 = [lista[index] for index in object2]

    if len(object2) > len(object1):
        odciete = object1_1
        glowny = object2_2
    else:
        odciete = object2_2
        glowny = object1_1
    return([glowny,odciete,najkrotsza])
        



def generalizuj(budynek):
    
    ID = budynek[1]
    budynek = budynek[0]
    w = len(budynek)-1

    nr_odcietego = 1

    lista_odcietych = []
    
    if not len(create_lista_przekatnych(budynek)) == 0:
        
        while w > k2:
            
            budynek = clear_list(budynek)

            temp_budynek = budynek
            
            w = len(budynek)-1

          
            if not len(create_lista_przekatnych(budynek)) == 0:

            
                if w > k2:
               
                        budynek,odciety,przekatna = delete_points(budynek)[0],delete_points(budynek)[1],delete_points(budynek)[2]
                        
     
                        if create_arcpy_line([temp_budynek[przekatna[1]],temp_budynek[przekatna[2]]]).within(create_arcpy_polygon(temp_budynek)):    
                            odciety = [odciety,nr_odcietego,1]
                        else:
                            odciety = [odciety,nr_odcietego,0]

                        
                        lista_odcietych.append(odciety)
                        
                   
                        nr_odcietego = nr_odcietego + 1
            else:
                break
            w = len(budynek)-1

    budynek = [budynek,ID]
    lista_odcietych = [lista_odcietych,ID]
    return(budynek,lista_odcietych)




def create_arcpy_line(line):
    arcpy_line = arcpy.Polyline(arcpy.Array([arcpy.Point(line[0][0],line[0][1]),arcpy.Point(line[1][0],line[1][1])]))
    return(arcpy_line)




def create_arcpy_polygon(polygon):
    arcpy_polygon = arcpy.Polygon(arcpy.Array([arcpy.Point(ppoint[0],ppoint[1]) for ppoint in polygon]))
    return(arcpy_polygon) 



    
tolerancja = 10
k=1
k2=4
id_field_name = 'id'

budynki = r'C:\Users\fitzu\Desktop\Python\Egzamin\budynki.shp'

print('Czytanie geometrii')
print(' ')
kursor_czytania = arcpy.da.SearchCursor(budynki, ['SHAPE@', id_field_name])
lista_budynkow = []
lista_odrzuconych = []
for row_czy in kursor_czytania:
    try:
        geometria = czyt(row_czy[0])
        lista2 = [geometria,row_czy[1]]
        lista_budynkow.append(lista2)
    except:
        lista_odrzuconych.append(row_czy[1])

print('Generalizacja')
print(' ')
wynik_lista = []
wynik_lista_odcietych = []
for poligon in lista_budynkow:
    print('Proces dla budynku o numerze' + str(poligon[1]))
    try:
        wynik_lista.append(generalizuj(poligon)[0])
        wynik_lista_odcietych.append(generalizuj(poligon)[1])
    except:
        lista_odrzuconych.append(poligon[1])


print(' ')
print('Zapisywanie')
print(' ')
wynik_shp = arcpy.CreateFeatureclass_management(r'C:\Users\fitzu\Desktop\Python\Egzamin','wynik.shp','POLYGON',budynki)
wynik_shp_odciete = arcpy.CreateFeatureclass_management(r'C:\Users\fitzu\Desktop\Python\Egzamin','wynik_odciete.shp','POLYGON')
arcpy.AddField_management(wynik_shp_odciete,'id_budynku','SHORT')
arcpy.AddField_management(wynik_shp_odciete,'id_odciete','SHORT')
arcpy.AddField_management(wynik_shp_odciete,'In_Out','SHORT')


with arcpy.da.InsertCursor(wynik_shp, ['SHAPE@', id_field_name]) as cursor:
    for poligon in wynik_lista:
        cursor.insertRow([poligon[0],poligon[1]])

with arcpy.da.InsertCursor(wynik_shp_odciete, ['SHAPE@', 'id_budynku', 'id_odciete','In_Out']) as cursor:
    for budynek in wynik_lista_odcietych:
        for odciety in budynek[0]:
            id_budynku = budynek[1]
            cursor.insertRow([odciety[0],id_budynku,odciety[1],odciety[2]])



print('Lista odrzuconych budynków: ' + str(lista_odrzuconych))

