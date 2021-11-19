from tkinter import *
from pydicom import *
import xml.etree.ElementTree as ET
from PIL import _imaging
from tkinter import messagebox
from datetime import date
from pathlib import Path




program = Tk()

program.geometry('600x400')
program.title('GLAVNI MENI')


lista = Listbox(program,width=30,height=10)

lista.place(x=0,y=0)






# PREGLEDI

def pregledi():
    novi = Tk()
    novi.geometry('800x400')
    novi.title('Pregledi')

    lista_pr = Listbox(novi, width=30, height=10)
    lista_pr.place(x=0, y=0)



    for x in pod:
        if temp_lbo==x[0].text:
            for i in x[4]:
                lista_pr.insert(END,i[1].text+'|'+i[2].text+'|'+i[0].text)


    def detalji():
        selection = lista_pr.curselection()

        if not selection:
            messagebox.showinfo('Obavestenje','Niste izabrali nijedan pregled!')

        else:

            od = lista_pr.get(ANCHOR)
            temp_od = od[-2:]
            preg = Text(novi, width=50, height=10)
            preg.place(x=250, y=0)
            for x in pod:
                for i in x[4]:
                    if temp_od == i[0].text:
                        preg.insert(END, 'Datum pregleda:' + ' ' + i[1].text+ '\n')
                        preg.insert(END, 'Vrsta pregleda:' + ' ' + i[2].text+ '\n')
                        preg.insert(END, 'Lekar:' + ' ' + i[3].text+ '\n')
                        preg.insert(END, 'Dijagnoza:' + ' ' + i[4].text+ '\n')
                        preg.insert(END,'Snimak:'+' '+i[5].text)
                        preg.config(state=DISABLED)
            text1 = Text(novi, width=25, height=1)
            text1.insert(END, 'Unesite putanju do snimka')
            text1.place(x=300, y=200)
            text1.config(state=DISABLED)

            za_sni = Entry(novi, width=65)
            za_sni.place(x=300, y=220)

        def otvori_snimak():
            import pydicom as dicom
            # import matplotlib.pylab as plt
            global put
            put =za_sni.get()
            nov1 = Tk()
            nov1.geometry('320x250')
            nov1.title('DICOM')
            try:
                slika = dicom.read_file(put)

                f1 = LabelFrame(nov1, text='DICOM PODACI')
                f1.grid(row=1, column=1)

                t1 = Text(f1, width=40, height=10)
                t1.grid(row=1, column=1)

                t1.insert(END, 'ID:' + str(slika[0x10, 0x20].value) + '\n')
                t1.insert(END, 'Ime i prezime:' + str(slika[0x10, 0x10].value) + '\n')
                t1.insert(END, 'Datum rodjenja:' + str(slika[0x10, 0x30].value) + '\n')
                t1.insert(END, 'ID pregleda:'+str(slika.StudyID)+'\n')
                t1.insert(END, 'Datum pregleda:'+str(slika.StudyDate)+'\n')
                t1.insert(END, 'Tip pregleda:'+str(slika.Modality)+'\n')
                t1.insert(END, 'Izvestaj:'+str(slika.StudyDescription)+'\n')
                t1.insert(END, 'Lekar:'+str(slika[0x08,0x90].value)+'\n')

                have_PIL = True
                try:
                    import PIL.Image
                except ImportError:
                    have_PIL = False

                have_numpy = True
                try:
                    import numpy as np
                except ImportError:
                    have_numpy = False

                def get_LUT_value(data, window, level):
                    """Apply the RGB Look-Up Table for the given
                       data and window/level value."""
                    if not have_numpy:
                        raise ImportError("Numpy is not available."
                                          "See http://numpy.scipy.org/"
                                          "to download and install")
                    try:
                        window = window[0]
                    except TypeError:
                        pass
                    try:
                        level = level[0]
                    except TypeError:
                        pass

                    return np.piecewise(data,
                                        [data <= (level - 0.5 - (window - 1) / 2),
                                         data > (level - 0.5 + (window - 1) / 2)],
                                        [0, 255, lambda data: ((data - (level - 0.5)) /
                                                               (window - 1) + 0.5) * (255 - 0)])

                def get_PIL_image(dataset):
                    """Get Image object from Python Imaging Library(PIL)"""
                    if not have_PIL:
                        raise ImportError("Python Imaging Library is not available. "
                                          "See http://www.pythonware.com/products/pil/ "
                                          "to download and install")

                    if ('PixelData' not in dataset):
                        raise TypeError("Cannot show image -- DICOM dataset does not have "
                                        "pixel data")
                    # can only apply LUT if these window info exists
                    if ('WindowWidth' not in dataset) or ('WindowCenter' not in dataset):
                        bits = dataset.BitsAllocated
                        samples = dataset.SamplesPerPixel
                        if bits == 8 and samples == 1:
                            mode = "L"
                        elif bits == 8 and samples == 3:
                            mode = "RGB"
                        elif bits == 16:
                            # not sure about this -- PIL source says is 'experimental'
                            # and no documentation. Also, should bytes swap depending
                            # on endian of file and system??
                            mode = "I;16"
                        else:
                            raise TypeError("Don't know PIL mode for %d BitsAllocated "
                                            "and %d SamplesPerPixel" % (bits, samples))

                        # PIL size = (width, height)
                        size = (dataset.Columns, dataset.Rows)

                        # Recommended to specify all details
                        # by http://www.pythonware.com/library/pil/handbook/image.htm
                        im = PIL.Image.frombuffer(mode, size, dataset.PixelData,
                                                  "raw", mode, 0, 1)

                    else:
                        image = get_LUT_value(dataset.pixel_array, dataset.WindowWidth,
                                              dataset.WindowCenter)
                        # Convert mode to L since LUT has only 256 values:
                        #   http://www.pythonware.com/library/pil/handbook/image.htm
                        im = PIL.Image.fromarray(image).convert('L')

                    return im

                def show_PIL(dataset):
                    """Display an image using the Python Imaging Library (PIL)"""
                    im = get_PIL_image(dataset)
                    im.show()

                show_PIL(slika)

                def izm_dicom():
                    nov2 = Tk()
                    nov2.geometry('600x450')
                    nov2.title('Izmeni podatke u DICOM')

                    ds = dicom.read_file(put)
                    im = str(ds[0x10,0x10].value)
                    ime = im.split()

                    dat = str(ds[0x10, 0x30].value)
                    dan = dat[:2]
                    mes = dat[3:5]
                    god = dat[-4:]

                    dani = int(dan)
                    mesi = int(mes)
                    godi = int(god)

                    dat_dan = date.today()
                    dat_s = str(dat_dan)
                    god_s = dat_s[:4]
                    mes_s = dat_s[5:7]
                    dan_s = dat_s[-2:]


                    godi_sada = int(god_s)
                    dani_sada = int(dan_s)
                    mesi_sada = int(mes_s)


                    id_pr = str(ds[0x20,0x10].value)
                    dat_pr = str(ds[0x08,0x20].value)
                    dan_pr = dat_pr[:2]
                    mes_pr = dat_pr[3:5]
                    god_pr = dat_pr[-4:]
                    mod_pr = str(ds[0x08,0x60].value)
                    opis = str(ds.StudyDescription)
                    lek_pr = str(ds[0x08,0x90].value)

                    fajl_lekari = ET.parse('lekari.xml')
                    root = fajl_lekari.getroot()

                    imena_l = []

                    im = fajl_lekari.findall('lekar/ime')
                    pr = fajl_lekari.findall('lekar/prezime')

                    duz = len(im)

                    for i in range(duz):
                        imena_l.append(im[i].text + ' ' + pr[i].text)




                    f2 = LabelFrame(nov2,text='Podaci pacijenta')
                    f2.place(in_=nov2,anchor='c',relx=.5,rely=.2)

                    Label(f2, text='Ime:').grid(row=1,column=1)
                    txt1 = Entry(f2,width=10)
                    txt1.grid(row=1,column=2)
                    txt1.insert(END,ime[0])


                    Label(f2,text='Prezime:').grid(row=3,column=1)
                    txt2 = Entry(f2,width=10)
                    txt2.grid(row=3,column=2)
                    txt2.insert(END,ime[1])

                    Label(f2,text='Datum rodjenja').grid(row=5,column=2)
                    Label(f2,text='Dan').grid(row=6,column=1)
                    Label(f2,text='Mesec').grid(row=6,column=2)
                    Label(f2,text='Godina').grid(row=6,column=3)
                    s1=Spinbox(f2,from_=1,to=31,width=2)
                    s1.grid(row=7,column=1)
                    s1.delete(0,END)
                    s1.insert(0,dan)
                    s2=Spinbox(f2,from_=1,to=12,width=2)
                    s2.grid(row=7,column=2)
                    s2.delete(0,END)
                    s2.insert(0,mes)
                    s3=Spinbox(f2,from_=1900,to=god_s,width=4)
                    s3.grid(row=7,column=3)
                    s3.delete(0,END)
                    s3.insert(0,god)


                    f3=LabelFrame(nov2,text='Podaci o pregledu')
                    f3.place(in_=nov2,anchor='c',relx=.5,rely=.6,width=500)
                    Label(f3,text='Tip pregleda:').grid(row=1,column=1)

                    tipovi = ['EKG','MRI','Kontrola','Sistematski']

                    temp_iz = tipovi.index(mod_pr)
                    iz1 = StringVar(f3)
                    iz1.set(tipovi[temp_iz])
                    tip_p = OptionMenu(f3,iz1,*tipovi)
                    tip_p.grid(row=1,column=2)

                    Label(f3,text='Opis pregleda:').grid(row=3,column=1)
                    txt_opis = Entry(f3,width=50)
                    txt_opis.insert(END,opis)
                    txt_opis.grid(row=3,column=2)

                    Label(f3,text='Lekar:').grid(row=7,column=1)
                    temp_lek = imena_l.index(lek_pr)
                    iz2 = StringVar(f3)
                    iz2.set(imena_l[temp_lek])
                    lek_p = OptionMenu(f3,iz2,*imena_l)
                    lek_p.grid(row=7,column=2)

                    Label(f3,text='Datum pregleda').grid(row=8,column=2)
                    Label(f3,text='Dan').grid(row=9,column=1)
                    Label(f3,text='Mesec').grid(row=9,column=2)
                    Label(f3,text='Godina').grid(row=9,column=3)

                    s4=Spinbox(f3,from_=1,to=31,width=2)
                    s4.grid(row=10,column=1)
                    s4.delete(0,END)
                    s4.insert(END,dan_pr)

                    s5 = Spinbox(f3,from_=1,to=12,width=2)
                    s5.grid(row=10,column=2)
                    s5.delete(0,END)
                    s5.insert(END,mes_pr)

                    s6 = Spinbox(f3,from_=godi,to=god_s,width=4)
                    s6.grid(row=10,column=3)
                    s6.delete(0,END)
                    s6.insert(END,god_pr)

                    def pod_izmeni():
                        # za pacijenta
                        ime_iz = txt1.get()
                        pr_iz = txt2.get()
                        dan_iz = s1.get()
                        mes_iz = s2.get()
                        god_iz = s3.get()

                        # za pregled
                        tip_iz = iz1.get()
                        opis_iz = txt_opis.get()
                        lek_iz = iz2.get()
                        s4_iz = s4.get()
                        s5_iz = s5.get()
                        s6_iz = s6.get()

                        if len(ime_iz)<2:
                            messagebox.showinfo('Obavestenje','Niste uneli ime!')
                        elif len(pr_iz)<2:
                            messagebox.showinfo('Obavestenje','Niste uneli prezime!')
                        elif len(opis_iz)<5:
                            messagebox.showinfo('Obavestenje','Niste opisali pregled!')
                        elif int(s6_iz)>godi_sada:
                            messagebox.showinfo('Obavestenje','Neodgovarajuca godina')
                        elif int(s6_iz)<godi:
                            messagebox.showinfo('Obavestenje','Neodgovarajuca godina!')
                        elif int(god_iz)>godi_sada:
                            messagebox.showinfo('Obavestenje','Neodgovarajuca godina rodjenja!')
                        elif int(s6_iz)==godi_sada:
                            if int(s5_iz)>mesi:
                                messagebox.showinfo('Obavestenje','Neodgovarajuci datum!')
                            elif int(s5_iz)==mesi:
                                if int(s4_iz)<dani:
                                    pass
                                else:
                                    messagebox.showinfo('Obavestenje','Neodgovarajuci datum!')
                            else:
                                pass


                        else:

                            imm = ime_iz+' '+pr_iz
                            ds[0x10,0x10].value=imm
                            if len(dan_iz)<2:
                                dan_iz='0'+dan_iz
                            else:
                                pass
                            if len(mes_iz)<2:
                                mes_iz='0'+mes_iz
                            else:
                                pass


                            if len(s4_iz)<2:
                                dan_iz = '0'+dan_iz
                            else:
                                pass
                            if len(s5_iz)<2:
                                s5_iz='0'+s5_iz
                            else:
                                pass
                            ds[0x10,0x30].value=dan_iz+'.'+mes_iz+'.'+god_iz
                            ds[0x08,0x60].value=tip_iz
                            ds.StudyDescription=opis_iz
                            ds[0x08,0x90].value=lek_iz
                            ds[0x08,0x20].value=s4_iz+'.'+s5_iz+'.'+s6_iz
                            ds.save_as('slike/slika.dcm')
                            messagebox.showinfo('Obavestenje','Uspesno ste promenili podatke!')
                            nov2.destroy()








                    but6 = Button(nov2,text='Sacuvaj izmene',command=pod_izmeni)
                    but6.grid(row=1,column=1)






                    nov2.mainloop()

                but5 = Button(nov1, text='Izmeni podatke',command=izm_dicom)
                but5.grid(row=5, column=1)





            except:
                  messagebox.showinfo('Obavestenje','Ne postoji navedeni snimak!')

            but4 = Button(novi, text='Otvori snimak', command=otvori_snimak)
            but4.place(x=620, y=218)

# DODAJ PREGLED


    def izbrisi_preg():
        fajl = ET.parse('proba.xml')
        root = fajl.getroot()
        selection = lista_pr.curselection()

        if not selection:
            messagebox.showinfo('Obavestenje', 'Niste izabrali nijedan pregled!')
        else:
            od = lista_pr.get(ANCHOR)
            temp_od = od[-2:]
            for i in root:
                for j in i[4]:
                    if temp_od == j[0].text:
                        i[4].remove(j)
                        fajl.write('proba.xml')
                        messagebox.showinfo('Obavestenje', 'Izbrisali ste pregled!')








    def dodaj_pregled():
        from datetime import date
        import tkinter as tk


        nov = Tk()
        nov.geometry('400x400')
        nov.title('Dodavanje pregleda')



        datum = date.today()
        god_sada = str(datum)
        god_sada = int(god_sada[:4])


        fajl_lekari = ET.parse('lekari.xml')
        root = fajl_lekari.getroot()

        imena_l = []

        im = fajl_lekari.findall('lekar/ime')
        pr = fajl_lekari.findall('lekar/prezime')

        duz=len(im)

        for i in range(duz):
            imena_l.append(im[i].text+' '+pr[i].text)


        tk.Label(nov, text='Dan:').grid(row=0,column=1)
        tk.Label(nov, text='Mesec:').grid(row=1,column=1)
        tk.Label(nov, text='Godina:').grid(row=2,column=1)
        tk.Label(nov, text='Vrsta pregleda:').grid(row=3,column=1)
        tk.Label(nov, text='Dijagnoza:').grid(row=4,column=1)
        tk.Label(nov, text='Snimak:').grid(row=5,column=1)
        tk.Label(nov, text='Lekar:').grid(row=6,column=1)

        dans = Spinbox(nov, from_=1, to=31)
        dans.grid(row=0, column=5)

        mes = Spinbox(nov, from_=1, to=12)
        mes.grid(row=1, column=5)

        god = Spinbox(nov, from_=0, to=god_sada)
        god.grid(row=2, column=5)

        vrste_preg = ['EKG','MRI','Kontrola','Sistematski']
        vr_iz = StringVar(nov)
        vr_p = OptionMenu(nov,vr_iz,*vrste_preg)
        vr_p.grid(row=3,column=5)

        dij = Entry(nov,width=50)
        dij.grid(row=4,column=5)

        sni = Entry(nov,width=30)
        sni.grid(row=5,column=5)


        izabran = StringVar(nov)


        lek = OptionMenu(nov,izabran,*imena_l)

        lek.grid(row=6,column=5)






        def provera_pregleda():
            from random import randint
            import os.path
            from tkinter import messagebox

            id = randint(10,99)
            fajl = ET.parse('proba.xml')
            root = fajl.getroot()

            id_p = []

            for i in root:
                for j in i[4]:
                    id_p.append(j[0].text)

            while id in id_p:
                id = randint(10,99)
            else:
                pass




            dan_p = dans.get()
            mes_p = mes.get()

            if len(dan_p) == 1:
                dan_p = '0' + dan_p
            else:
                pass
            if len(mes_p) == 1:
                mes_p = '0' + mes_p
            else:
                pass

            god_p = god.get()
            vr_pp = vr_iz.get()
            lek_p =izabran.get()
            dij_p = dij.get()
            sni_p = sni.get()
            id = str(id)






            danas = date.today()

            dan_r = rodj[:2]
            mes_r = rodj[3:5]
            god_r = rodj[-4:]

            dat_r = date(int(god_r), int(mes_r), int(dan_r))







            if len(god_p)<4:
                messagebox.showinfo('Obavestenje','Niste uneli godinu!')
                nov.quit()


            else:
                global dat_p
                dat_p = date(int(god_p), int(mes_p), int(dan_p))
                if dat_p > danas or dat_p < dat_r:
                    messagebox.showinfo('Obavestenje', 'Neodgovarajuci datum!')
            if not lek_p:
                messagebox.showinfo('Obavestenje','Niste izabrali lekara!')
            elif not vr_pp:
                messagebox.showinfo('Obavestenje','Niste izabrali vrstu pregleda')

            else:
                attrib = {}
                ele = ET.Element('pregled', attrib)
                subel1 = ET.SubElement(ele, 'ID')
                subel1.text = id

                subel2 = ET.SubElement(ele, 'datum')
                subel2.text = dan_p + '.' + mes_p + '.' + god_p

                subel3 = ET.SubElement(ele, 'vrsta_pregleda')
                subel3.text = vr_pp

                subel4 = ET.SubElement(ele, 'lekar')
                subel4.text = lek_p

                subel5 = ET.SubElement(ele, 'dijagnoza')
                subel5.text = dij_p

                if len(sni_p) < 4:
                    subel6 = ET.SubElement(ele, 'snimak')
                    subel6.text = '-'
                else:
                    subel6 = ET.SubElement(ele, 'snimak')
                    sni_p = str(sni_p)
                    subel6.text = sni_p

                for i in root:
                    if i[0].text == temp_lbo:
                        i[4].append(ele)
                        fajl.write('proba.xml')
                        messagebox.showinfo('Obavestenje', 'Uspesno ste dodali novi pregled!')
                        nov.quit()


        but = Button(nov,text='Sacuvaj',command=provera_pregleda)
        but.grid(row=10,column=5)









        nov.mainloop()

    def izmeni_pregled():
        import tkinter as tk

        nov_izmena = Tk()
        nov_izmena.geometry('500x250')
        nov_izmena.title('Izmena pregleda')
        selection = lista_pr.curselection()


        if not selection:
            messagebox.showinfo('Obavestenje','Niste izabrali ni jedan pregled!')
            nov_izmena.destroy()

        else:

            fajl = ET.parse('proba.xml')
            root1 = fajl.getroot()

            temp_id = lista_pr.get(ANCHOR)
            temp_id = temp_id[-2:]
            for i in root1:
                for j in i[4]:
                    if j[0].text==temp_id:
                        temp_dat = j[1].text
                        temp_vp = j[2].text
                        temp_lek = j[3].text
                        temp_dij = j[4].text
                        temp_sni = j[5].text



                        dan = Spinbox(nov_izmena, from_=1,to=31)
                        dan.grid(row=1, column=5)
                        dan.delete(0,END)
                        dan.insert(0,temp_dat[:2])

                        mes = Spinbox(nov_izmena,from_=1,to=12)
                        mes.grid(row=2,column=5)
                        mes.delete(0,END)
                        mes.insert(0,temp_dat[3:5])

                        god = Spinbox(nov_izmena,from_=1900,to=2100)
                        god.grid(row=3,column=5)
                        god.delete(0,END)
                        god.insert(0,temp_dat[-4:])





                        vr_p = Entry(nov_izmena, width=50)
                        vr_p.grid(row=4, column=5)
                        vr_p.insert(END,temp_vp)

                        dij = Entry(nov_izmena, width=50)
                        dij.grid(row=5, column=5)
                        dij.insert(END,temp_dij)

                        sni = Entry(nov_izmena, width=50)
                        sni.grid(row=6, column=5)
                        sni.insert(END,temp_sni)

                        fajl_lekari = ET.parse('lekari.xml')
                        root = fajl_lekari.getroot()

                        imena_l = []

                        im = fajl_lekari.findall('lekar/ime')
                        pr = fajl_lekari.findall('lekar/prezime')

                        duz = len(im)

                        for i in range(duz):
                            imena_l.append(im[i].text + ' ' + pr[i].text)

                        ind = imena_l.index(temp_lek)

                        izabran = StringVar(nov_izmena)
                        izabran.set(imena_l[ind])

                        lek = OptionMenu(nov_izmena, izabran, *imena_l)
                        lek.grid(row=7, column=5)

                        tk.Label(nov_izmena, text='Lekar:').grid(row=7, column=1)
                        tk.Label(nov_izmena, text='Dan:').grid(row=1, column=0)
                        tk.Label(nov_izmena, text='Mesec:').grid(row=2, column=0)
                        tk.Label(nov_izmena, text='Godina:').grid(row=3, column=0)

                        tk.Label(nov_izmena,text='Vrsta pregleda:').grid(row=4,column=0)
                        tk.Label(nov_izmena, text='Dijagnoza:').grid(row=5, column=0)
                        tk.Label(nov_izmena, text='Snimak:').grid(row=6, column=0)





        def izm_preg():
            dan_p = dan.get()
            mes_p = mes.get()
            god_p = god.get()
            vr_pp = vr_p.get()
            lek_p = izabran.get()
            dij_p = dij.get()
            sni_p = sni.get()
            danas = date.today()

            if len(sni_p)>4:
                    put = Path(sni_p)
                    if put.is_file():
                        pass
                    else:
                        messagebox.showinfo('Obavestenje', 'Ne postoji snimak!')
                        sni_p = '-'
            else:
                sni_p='-'



            # if len(dan_p)<2:
            #     dan_p = '0'+dan_p
            # elif len(dan_p)>2:
            #     messagebox.showinfo('Obavestenje','Neispravan datum!')
            # elif len(mes_p)<2:
            #     mes_p = '0'+mes_p
            # elif len(mes_p)>2:
            #     messagebox.showinfo('Obavestenje','Neispravan datum!')
            moj_datum = date(int(god_p), int(mes_p), int(dan_p))
            if len(god_p)<4 or len(god_p)>4:
                messagebox.showinfo('Obavestenje','Neispravan datum!')
            elif moj_datum > danas:
                messagebox.showinfo('Obavestenje', 'Neispravan datum!')
            elif len(vr_pp) < 2:
                messagebox.showinfo('Obavestenje', 'Za vrstu pregleda morate uneti bar dva karaktera!')
            elif len(dij_p) < 2:
                messagebox.showinfo('Obavestenje', 'Za dijagnozu morate uneti bar dva karaktera!')


            else:

                moj_datum = str(moj_datum)
                moj_datum = moj_datum[-2:]+'.'+moj_datum[5:7]+'.'+moj_datum[:4]
                for i in root1:
                    for j in i[4]:
                        if temp_id==j[0].text:
                            j[1].text = moj_datum
                            j[2].text = vr_pp
                            j[3].text = lek_p
                            j[4].text = dij_p
                            j[5].text = sni_p
                            fajl.write('proba.xml')
                            messagebox.showinfo('Obavestenje','Uspesno ste izmenili pregled!')
                            nov_izmena.destroy()
        try:
           but = Button(nov_izmena, text='Sacuvaj izmene', command=izm_preg)
           but.grid(row=9, column=5)
        except:
            pass


        nov_izmena.mainloop()













    but = Button(novi,text='Detalji pregleda',command=detalji)
    but.place(x=0,y=200)

    but2 = Button(novi,text='Dodaj pregled',command=dodaj_pregled)
    but2.place(x=0,y=250)

    but3 = Button(novi,text='Izmeni pregled',command=izmeni_pregled)
    but3.place(x=0,y=300)

    but4 = Button(novi,text='Izbrisi pregled',command=izbrisi_preg)
    but4.place(x=0,y=350)


    novi.mainloop()





# GLAVNI MENI




def prvi():
    selection = lista.curselection()
    if not selection:
        messagebox.showinfo('Obavestenje','Niste izabrali nijednog pacijenta!')
    else:
        od = lista.get(ANCHOR)
        global temp_lbo
        temp_lbo = od[:11]
        prvi = Text(program, width=30, height=10)
        prvi.place(x=300, y=0)
        for x in pod:
            if temp_lbo == x[0].text:
                prvi.insert(END, 'LBO:' + ' ' + temp_lbo + '\n')
                prvi.insert(END, 'Ime:' + ' ' + x[1].text + '\n')
                prvi.insert(END, 'Prezime:' + ' ' + x[2].text + '\n')
                prvi.insert(END, 'Datum rodjenja:' + ' ' + x[3].text + '\n')
                global rodj
                global ime_pacijenta
                global prezime

                ime_pacijenta=x[1].text
                prezime=x[2].text

                rodj = x[3].text
                prvi.config(state=DISABLED)


                preg = Button(program, text='Pregledi', command=pregledi)
                preg.place(x=300, y=200)








# DODAVANJE NOVOG PACIJENTA

def drugi():
    from datetime import date
    import tkinter as tk
    from tkinter import messagebox
    import xml.etree.ElementTree as ET

    novi2 = Tk()
    novi2.title('Dodavanje novog pacijenta')
    novi2.geometry('300x200')
    tk.Label(novi2,text='LBO:').grid(row=0)
    tk.Label(novi2,text='Ime:').grid(row=1)
    tk.Label(novi2,text='Prezime:').grid(row=2)
    tk.Label(novi2,text='Dan:').grid(row=3)
    tk.Label(novi2,text='Mesec:').grid(row=4)
    tk.Label(novi2,text='Godina:').grid(row=5)


    datum = date.today()
    god_sada = str(datum)
    god_sada = int(god_sada[:4])



    fajl = ET.parse('proba.xml')
    lbo1 = []
    broj = fajl.findall('pacijent/LBO')
    for i in broj:
        lbo1.append(i.text)


    lbo = Entry(novi2, width=20)
    lbo.grid(row=0, column=1)

    ime = Entry(novi2,width=20)
    ime.grid(row=1,column=1)

    pre = Entry(novi2,width=20)
    pre.grid(row=2,column=1)

    dans = Spinbox(novi2,from_=1,to=31)
    dans.grid(row=3,column=1)

    mes= Spinbox(novi2,from_=1,to=12)
    mes.grid(row=4,column=1)

    god = Spinbox(novi2,from_=1900,to=god_sada)
    god.grid(row=5,column=1)

# DODAVANJE NOVOG PACIJENTA DA LI JE SVE OK?

    def provera():
        lbo_p = lbo.get()
        ime_p = ime.get()
        pre_p = pre.get()
        dan_p = dans.get()
        mes_p = mes.get()
        god_p = god.get()

        if len(dan_p)==1:
            dan_p = '0'+dan_p
        else:
            pass
        if len(mes_p)==1:
            mes_p = '0'+mes_p
        else:
            pass

        dan = date.today()
        if len(god_p)<4:
            messagebox.showinfo('Datum','Niste uneli godinu!')
        else:
            dat_p = date(int(god_p), int(mes_p), int(dan_p))
        if len(lbo_p)!=11 or lbo_p in lbo1:
            messagebox.showinfo('LBO','Neodgovarajuci LBO!')
        elif len(ime_p)<2:
            messagebox.showinfo('Ime','Neodgovarajuce ime!')
        elif len(pre_p)<2:
            messagebox.showinfo('Prezime','Neodgovarajuce prezime!')
        elif dat_p>datum:
            messagebox.showinfo('Datum','Datum nije validan')
        else:
            tree=ET.parse('proba.xml')
            root = tree.getroot()

            attrib = {}

            e1 = root.makeelement('pacijent',attrib)
            root.append(e1)

            se = root[0].makeelement('LBO',attrib)
            lb = ET.SubElement(e1,'LBO')
            lb.text=lbo_p

            se1 = root[0].makeelement('Ime',attrib)
            im = ET.SubElement(e1,'Ime')
            im.text=ime_p

            se2 = root[0].makeelement('Prezime',attrib)
            pr = ET.SubElement(e1,'Prezime')
            pr.text=pre_p

            se3 = root[0].makeelement('Datum rodjenja:',attrib)
            d = ET.SubElement(e1,'Datum_rodjenja')
            d.text = dan_p+'.'+mes_p+'.'+god_p

            se4 = root[0].makeelement('Pregledi',attrib)
            preg = ET.SubElement(e1,'Pregledi')

            tree.write('proba.xml')

            messagebox.showinfo('Obavestenje','Uspesno ste uneli novog pacijenta!')



# TREBA VIDETI STA SA PREGLEDIMA DA LI IH OVDE DODAVATI ILI NA KOMANDU PREGLEDI !
# UNOS JE DOBAR SVE FUNKCIONISE JOS STOJI PROBA.XML ZBOG PREGLEDA!







    sacuvaj = Button(novi2,text='Sacuvaj',command=provera)
    sacuvaj.grid(row=8,column=1)


# izmeni podatke pacijenta
def izmeni_podatke():
    selection = lista.curselection()
    if not selection:
        messagebox.showinfo('Obavestenje','Niste izabrali pacijenta!')
    else:
        od = lista.get(ANCHOR)
        global temp_lbo
        temp_lbo=od[:11]
        fajl = ET.parse('proba.xml')
        root = fajl.getroot()

        for i in root:
            if i[0].text == temp_lbo:
                nov = Tk()
                nov.geometry('400x200')
                nov.title('Izmeni podatke pacijenta')

                ime = i[1].text
                pre = i[2].text
                dat = i[3].text
                dan = int(dat[:2])
                mes = int(dat[3:5])
                god = int(dat[-4:])

                danas = date.today()
                danas = str(danas)
                dan_s = danas[-2:]
                mes_s = danas[6:7]
                god_s = danas[:4]


                Label(nov,text='Ime:').grid(row=1,column=1)
                Label(nov,text='Prezime').grid(row=4,column=1)
                Label(nov,text='Datum rodjenja').grid(row=7,column=2)
                Label(nov,text='Dan').grid(row=10,column=1)
                Label(nov,text='Mesec').grid(row=12,column=1)
                Label(nov,text='Godina').grid(row=14,column=1)

                e1 = Entry(nov,width=20)
                e1.grid(row=1,column=2)
                e1.insert(END,ime)

                e2 = Entry(nov,width=20)
                e2.grid(row=4,column=2)
                e2.insert(END,pre)

                e3 = Spinbox(nov,from_=1,to=31)
                e3.grid(row=10,column=2)
                e3.delete(0,END)
                e3.insert(END,dan)

                e4 = Spinbox(nov,from_=1,to=12)
                e4.grid(row=12,column=2)
                e4.delete(0,END)
                e4.insert(END,mes)

                e5 = Spinbox(nov,from_=1900,to=god_s)
                e5.grid(row=14,column=2)
                e5.delete(0,END)
                e5.insert(END,god)

                def provera():
                    im_p = e1.get()
                    pr_p = e2.get()
                    dan_p = e3.get()
                    mes_p = e4.get()
                    god_p = e5.get()

                    dat_p = date(int(god_p),int(mes_p),int(dan_p))
                    dat_p = str(dat_p)
                    dat_p = dat_p[-2:]+'.'+dat_p[5:7]+'.'+dat_p[:4]
                    print(dat_p)


                    if len(im_p)<2:
                        messagebox.showinfo('Obavestenje','Niste uneli ime!')
                    elif len(pr_p)<2:
                        messagebox.showinfo('Obavestenje','Niste uneli prezime!')
                    else:
                        for i in root:
                            if temp_lbo==i[0].text:
                                i[1].text = im_p
                                i[2].text = pr_p
                                i[3].text = dat_p
                                fajl.write('proba.xml')
                                messagebox.showinfo('Obavestenje','Uspesno ste promenili podatke pacijenta!')










                but = Button(nov,text='Sacuvaj podatke',command=provera).grid(row=20,column=4)





                nov.mainloop()



def pretrazi_lbo():
    fajl = ET.parse('proba.xml')
    root= fajl.getroot()
    lbo = []
    for i in root:
        lbo.append(i[0].text)




    nov = Tk()
    nov.geometry('200x50')
    nov.title('Pretrazi pacijenta po LBO')

    Label(nov,text='Unesite LBO:').grid(row=1,column=1)

    e1 = Entry(nov,width=15)
    e1.grid(row=1,column=3)



    def pretraga():
        trazi = e1.get()
        lbo = []
        for i in root:
            lbo.append(i[0].text)

        if trazi in lbo:
            duz = len(lbo)
            for i in range(duz):
                if trazi == lbo[i]:
                    ind = i
            lista.select_set(ind)
            nov.destroy()


        else:
            messagebox.showinfo('Obavestenje', 'Ne postoji pacijent sa tim LBO!')
            nov.destroy()









    but = Button(nov,text='Pretrazi',command=pretraga).grid(row=3,column=1)












prikaz_pacijent = Button(program,text='Podaci o pacijentu',command=prvi)
prikaz_pacijent.place(x=0,y=200)

dodaj = Button(program,text='Dodaj pacijenta',command=drugi)
dodaj.place(x=0,y=250)

izmena = Button(program,text='Izmeni podatke pacijenta',command=izmeni_podatke)
izmena.place(x=0,y=300)


pretraga = Button(program,text='Pretrazi pacijenta po LBO',command=pretrazi_lbo)
pretraga.place(x=0,y=350)

pacijenti = ET.parse('proba.xml')
pod = pacijenti.getroot()

lbo = []



for child in pod:
    lbo.append(child[0].text)


duz = len(lbo)


for i in range(duz):
    lista.insert(END,lbo[i])



program.mainloop()