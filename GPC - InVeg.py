#------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Nome: Gerador de Gáficos Por Coordenada - Indíces de Vegetação 
# Descrição: ferramenta construída para acelerar a criação de gráficos com valores de indice de vegetação, a partir dos dados extraídos via API, do Brasil Data Cube
# Autor: Lucas Matheus de Oliveira Ramos
# Data Versão Alpha: 31/01/2023
# E-mail: lucas.matheus@vegamonitoramento.com.br
#------------------------------------------------------------------------------------------------------------------------------------------------------------------#
from tkinter import *
from wtss import *
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from tkinter.filedialog import *
import os

root = Tk()
title_label = Label(root, text='Bem-vindo ao GPC \nIndice de Vegetação', font=("Arial", 25))
title_label.place(x=71, y=80)
label = Label(root, text='Selecione uma opção para prosseguir:')
label.place(x=110, y=300)


def manual_generate():
    global root
    root.destroy()
    root = Tk() 
    root.title("Gerador de Dados por Coordenadas")
    root.geometry("575x400")    

    months = [ "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"] #etc

    begin_month = StringVar(root)
    begin_month.set(months[0]) # default value

    select_begin = OptionMenu(root, begin_month, *months)
    select_begin.pack()
    select_begin.configure(border=0, bg="#c9c9c9", width=10, height=1)
    select_begin.place(x=120,y=74)

    begin_month_label = Label(root, text='Mês Inicial')
    begin_month_label.place(x=30,y=80)


    end_month = StringVar(root)
    end_month.set(months[0]) # default value

    select_end = OptionMenu(root, end_month, *months)
    select_end.pack()
    select_end.place(x=120,y=102)
    select_end.configure(border=0, bg="#c9c9c9", width=10, height=1)


    #Select relacionado ao Ano
    begin_year_value = StringVar(value=2001)
    begin_year = Spinbox( root, from_=2001, to=2023, textvariable=begin_year_value)
    begin_year.pack()
    begin_year.place(x=410,y=80)
    begin_year_label = Label(root, text='Ano Inicial')
    begin_year_label.place(x=340,y=80)
    
    #Select relacionado ao Mês
    end_month_label = Label(root, text='Mês Final')
    end_month_label.place(x=30,y=105)
    
    #Select relacionado ao Ano
    end_year_value = StringVar(value=2023)
    end_year = Spinbox( root, from_=2001, to=2023, textvariable=end_year_value)
    end_year.pack()
    end_year.place(x=410,y=105)
    end_year_label = Label(root, text='Ano Final')
    end_year_label.place(x=340,y=105)
    
    def generate_file(latitude, longitude):
        mes_inicio = ""
        mes_fim = ""
        for i in range(len(months)):
            # print(OPTIONS[i])
            if months[i] == begin_month.get():
                if (i + 1) <= 9:
                    mes_inicio = "0" + str(i + 1)
                else: 
                    mes_inicio = str(i + 1)
            
            if months[i] == end_month.get():
                if (i + 1) <= 9:
                    mes_fim = "0" + str(i + 1)
                else: 
                    mes_fim = str(i + 1)


        data_inicio = (begin_year_value.get() + "-{0}-01".format(mes_inicio))
        data_fim = (end_year_value.get() + "-{0}-28".format(mes_fim))

        veg_chosen = v.get()
        veg_chosen_myd = []
        veg_chosen_mod = []
             
        lat = float(latitude)
        lon = float(longitude)

        service = WTSS('https://brazildatacube.dpi.inpe.br/', access_token='rzOha21pXHFr8IUgadboyn4s62weFBVsnCGJk73qbj')

        coverage_myd = service['MYD13Q1-6']
        ts_myd = coverage_myd.ts(attributes=('EVI', 'NDVI'),
                                latitude=lat, longitude=lon,
                                start_date=data_inicio, end_date=data_fim) #Dados até 05/03/2023
        

        coverage_mod = service['MOD13Q1-6']
        ts_mod = coverage_mod.ts(attributes=('EVI', 'NDVI'),
                                latitude=lat, longitude=lon,
                                start_date=data_inicio, end_date=data_fim) #Dados até 05/03/2023


        if veg_chosen == 'EVI':
            veg_chosen_myd = ts_myd.EVI
            veg_chosen_mod = ts_mod.EVI
        else:
            veg_chosen_myd = ts_myd.NDVI
            veg_chosen_mod = ts_mod.NDVI

        time_myd = []
        for i in range(len(ts_myd.timeline)):
            x = ((ts_myd.timeline[i])[0:10]).split("-")

            if [i + 1] != len(ts_myd.timeline):
                    time_myd.append(x[0] + "-" + x[1] + "-" + x[2])
        
            veg_chosen_myd[i] = veg_chosen_myd[i] / 10000

        d = {veg_chosen: veg_chosen_myd}


        time_mod = []
        for i in range(len(ts_mod.timeline)):
            x_mod = ((ts_mod.timeline[i])[0:10]).split("-")

            if [i + 1] != len(ts_mod.timeline):
                time_mod.append(x_mod[0] + "-" + x_mod[1] + "-" + x_mod[2])

            veg_chosen_mod[i] = float(veg_chosen_mod[i] / 10000)
        
        for i in range(len(veg_chosen_mod)):
                    if len(veg_chosen_mod) != len(time_mod):
                        veg_chosen_mod.pop()

        dd = {veg_chosen: veg_chosen_mod}

        time = [*time_myd, *time_mod]
        time.sort()

        time_correct = []
        for i in range(len(time)):
            x = (time[i]).split("-")

            time_correct.append(x[2] + "-" + x[1] + "-" + x[0])
        df_myd= pd.DataFrame(data=d, index=time_myd)
        ds_mod = pd.DataFrame(data=dd, index=time_mod)
        frames = [df_myd, ds_mod]

        df_conc = pd.concat(frames)
        df_conc.index = df_conc.index.sort_values()

        path_name = "lat {0} e lon {1}".format(lat, lon)

        if not os.path.exists(path_name):
                    os.mkdir(path_name)

        titulo = '{0} - entre {1} e {2}'.format(veg_chosen, time_correct[0], time_correct[-1])
        
        size_graph = 0.0
        if len(time_correct) > 12:
            size_graph = (len(time_correct) / 2.4)
        else:
            size_graph = 6
        plt.figure(figsize=(size_graph,6)) 
        plt.plot(time_correct, df_conc[veg_chosen],color="green") 
        plt.title(titulo, pad=-40)        
        plt.xlabel('')
        plt.ylabel('{0}'.format(veg_chosen))
        plt.ylim(0, 1)
        plt.grid(True)
        plt.xticks(rotation=45, ha="right", rotation_mode="anchor") 
        plt.subplots_adjust(top=0.95, bottom=0.15)
        plt.savefig("./{0}/{1}.png".format(path_name, titulo))
        df_conc.to_csv("./{0}/{1}.csv".format(path_name, titulo))

        print("Arquivo Salvo com Sucesso!")


    v = StringVar(root, "1")


    values = {"EVI" : "EVI", "NDVI" : "NDVI"}

    for (text, value) in values.items():
        Radiobutton(root, text = text, variable = v,
            value = value).pack(side = TOP)
            
    Label(root, text="Latitude", background="#abf321", foreground="#009", anchor=W).place(x=25, y=200, width=150)
    lt=Entry(root)
    lt.place(x=30, y=220, width=200, height=20)
    
    Label(root, text="Longitude", background="#abf321", foreground="#009", anchor=W).place(x=325, y=200, width=150)
    long=Entry(root)
    long.place(x=330, y=220, width=200, height=20)
    
    generate_button = Button(root, text='Gerar Gráficos', command = lambda: generate_file(lt.get(), long.get()))
    generate_button.pack()
    generate_button.place(x=460, y=350)
    
    home_bt = Button(root, text='<- Voltar',command=home)
    home_bt.pack()
    home_bt.place(x=25, y=350)

def auto_generate():
    global root
    root.destroy()
    root = Tk() 
    root.title("Gerador de Dados por Coordenadas")
    root.geometry("575x400") 
    
    def generate_file(arquivos):
        mes_inicio = ""
        mes_fim = ""
        for i in range(len(months)):
            if months[i] == begin_month.get():
                if (i + 1) <= 9:
                    mes_inicio = "0" + str(i + 1)
                else: 
                    mes_inicio = str(i + 1)
            
            if months[i] == end_month.get():
                if (i + 1) <= 9:
                    mes_fim = "0" + str(i + 1)
                else: 
                    mes_fim = str(i + 1)

        data_inicio = (begin_year_value.get() + "-{0}-01".format(mes_inicio))
        data_fim = (end_year_value.get() + "-{0}-28".format(mes_fim))

        veg_chosen = v.get()
        veg_chosen_myd = []
        veg_chosen_mod = []
             
                      
        for arquivo in range(len(arquivos)):
            dados = pd.read_csv(arquivos[arquivo])

            print(arquivos)

            save_frame = pd.DataFrame()

            for i in range(len(dados)):
                lat = float(dados.lat[i])
                lon = float(dados.lon[i])
                id = dados.id[i]

                service = WTSS('https://brazildatacube.dpi.inpe.br/', access_token='rzOha21pXHFr8IUgadboyn4s62weFBVsnCGJk73qbj')

                coverage_myd = service['MYD13Q1-6']
                ts_myd = coverage_myd.ts(attributes=('EVI', 'NDVI'),
                                        latitude=lat, longitude=lon,
                                        start_date=data_inicio, end_date=data_fim) #Dados até 05/03/2023
                

                coverage_mod = service['MOD13Q1-6']
                ts_mod = coverage_mod.ts(attributes=('EVI', 'NDVI'),
                                        latitude=lat, longitude=lon,
                                        start_date=data_inicio, end_date=data_fim) #Dados até 05/03/2023


                if veg_chosen == 'EVI':
                    veg_chosen_myd = ts_myd.EVI
                    veg_chosen_mod = ts_mod.EVI
                else:
                    veg_chosen_myd = ts_myd.NDVI
                    veg_chosen_mod = ts_mod.NDVI

                time_myd = []
                for i in range(len(ts_myd.timeline)):
                    x = ((ts_myd.timeline[i])[0:10]).split("-")

                    if [i + 1] != len(ts_myd.timeline):
                            time_myd.append(x[0] + "-" + x[1] + "-" + x[2])
                
                    veg_chosen_myd[i] = veg_chosen_myd[i] / 10000


                time_mod = []
                for i in range(len(ts_mod.timeline)):
                    x_mod = ((ts_mod.timeline[i])[0:10]).split("-")

                    if [i + 1] != len(ts_mod.timeline):
                        time_mod.append(x_mod[0] + "-" + x_mod[1] + "-" + x_mod[2])

                    veg_chosen_mod[i] = float(veg_chosen_mod[i] / 10000)
                
                for i in range(len(veg_chosen_mod)):
                            if len(veg_chosen_mod) != len(time_mod):
                                veg_chosen_mod.pop()

                time = [*time_myd, *time_mod]
                time.sort()

                time_correct = []
                for i in range(len(time)):
                    x = (time[i]).split("-")

                    time_correct.append(x[2] + "-" + x[1] + "-" + x[0])


                df_myd= pd.DataFrame({
                    "codigo_monitoramento" : id,
                    "valor" : veg_chosen_myd, 
                    "data_processamento" : time_myd
                })
                
                ds_mod= pd.DataFrame({
                    "codigo_monitoramento" : id,
                    "valor" : veg_chosen_mod, 
                    "data_processamento" : time_mod
                })
                    
                    # data=[d], index=time_myd)
                # ds_mod = pd.DataFrame(data=[dd], index=time_mod)
                frames = [df_myd, ds_mod]

                df_conc = pd.concat(frames)
                df_conc.index = df_conc.index.sort_values()
                # df_conc.columns.values[df_conc.index] = 'Student_Age'
                # print(df_conc)
                # print(df_conc)

                titulo = 'ID {0} - {1}'.format(id, veg_chosen)
                
                split_path_name = arquivos[arquivo].split("/")
                path_name = (split_path_name[-1])[:-4]
                
                if not os.path.exists(path_name):
                    os.mkdir(path_name)
                

                save_frame = save_frame.append(df_conc, ignore_index=True)

            
                print("Arquivo Salvo com Sucesso!")
            print(save_frame)
            save_frame.to_csv("formatoo.csv")
    filenames = []

    def get_files():
        Tk().withdraw() # Isto torna oculto a root principal
        filename = askopenfilename() # Isto te permite selecionar um arquivo
        filenames.append(filename)

    sel_bt = Button(root, text='Selecionar Arquivos',command=get_files)
    sel_bt.pack()
    sel_bt.place(x=230 ,y=350)

    months = [ "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"] #etc

    begin_month = StringVar(root)
    begin_month.set(months[0]) # default value

    select_begin = OptionMenu(root, begin_month, *months)
    select_begin.pack()
    select_begin.configure(border=0, bg="#c9c9c9", width=10, height=1)
    select_begin.place(x=120,y=74)

    begin_month_label = Label(root, text='Mês Inicial')
    begin_month_label.place(x=30,y=80)


    end_month = StringVar(root)
    end_month.set(months[0])

    select_end = OptionMenu(root, end_month, *months)
    select_end.pack()
    select_end.place(x=120,y=102)
    select_end.configure(border=0, bg="#c9c9c9", width=10, height=1)

    #Select relacionado ao Ano
    begin_year_value = StringVar(value=2001)
    begin_year = Spinbox( root, from_=2001, to=2023, textvariable=begin_year_value)
    begin_year.pack()
    begin_year.place(x=410,y=80)
    begin_year_label = Label(root, text='Ano Inicial')
    begin_year_label.place(x=340,y=80)
    
    #Select relacionado ao Mês
    end_month_label = Label(root, text='Mês Final')
    end_month_label.place(x=30,y=105)
    
    #Select relacionado ao Ano
    end_year_value = StringVar(value=2023)
    end_year = Spinbox( root, from_=2001, to=2023, textvariable=end_year_value)
    end_year.pack()
    end_year.place(x=410,y=105)
    end_year_label = Label(root, text='Ano Final')
    end_year_label.place(x=340,y=105)

    v = StringVar(root, "1")

    values = {"EVI" : "EVI", "NDVI" : "NDVI"}

    for (text, value) in values.items():
        Radiobutton(root, text = text, variable = v,
            value = value).pack(side = TOP)
  
    generate_button = Button(root, text='Gerar Gráficos', command = lambda: generate_file(filenames))
    generate_button.pack()
    generate_button.place(x=460, y=350)
    
    home_bt = Button(root, text='<- Voltar',command=home)
    home_bt.pack()
    home_bt.place(x=25, y=350)

def home():
    global root
    root.destroy()
    root = Tk()
    title_label = Label(root, text='Bem-vindo ao GPC\nIndice de Vegetação', font=("Arial", 25))
    title_label.place(x=71, y=80)
    root.title("GPC - Indices de Vegetação")
    root.geometry("424x500") 

    label = Label(root, text='Selecione uma opção para prosseguir:')
    label.place(x=110, y=300)
    
    manual_generate_bt = Button(root, text='Gerar Dados Manualmente', command=manual_generate, 
                            border=0, bg="#c9c9c9", 
                            width=24, height=2)

    auto_generate_bt = Button(root, text='Gerar Dados Automaticamente', command=auto_generate, 
                            border=0, bg="#c9c9c9", 
                            width=24, height=2)

    manual_generate_bt.place(x=30,y=340)
    auto_generate_bt.place(x=220,y=340)
    root.mainloop()  


manual_generate_bt = Button(root, text='Gerar Dados Manualmente', command=manual_generate, 
                        border=0, bg="#c9c9c9", 
                        width=24, height=2)
auto_generate_bt = Button(root, text='Gerar Dados Automaticamente', command=auto_generate, 
                        border=0, bg="#c9c9c9", 
                        width=24, height=2)

manual_generate_bt.place(x=30,y=340)
auto_generate_bt.place(x=220,y=340)

root.geometry("424x500") # Largura x Altura
root.title("GPC - Indices de Vegetação")

root.mainloop()