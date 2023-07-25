import streamlit as st
from zipfile import ZipFile
from typing import Dict
import numpy as np
import pandas as pd
import plotly.express as px
import csv
import shutil
import os
import io
from PIL import Image

@st.cache_data
def get_static_store() -> Dict:
   """This dictionary is initialized once and can be used to store the files uploaded"""
   return {}

def app():
    global show_chart, show_df, fig

    if device == "Micsig":
        allMem = 87500
    elif device == "GWInstek":
        allMem = 5000
    cycleMem = allMem/cycle
    quarter = cycleMem/4
    numCycle = allMem/cycleMem

    df1 = pd.DataFrame((zip([],[],[])),columns =['deg', 'voltage_mV', 'kind'])

    for x in range(1, int(filecouple+1)):
        
        my_bar.progress(value= x/(filecouple))
        
        print("progress count: ", x)
       
        data_sinus = pd.read_csv("output/{}{}.csv".format(sine_name, x))
        if device == 'GWInstek':
            data_sinus = data_sinus.iloc[15:]
            data_sinus = pd.concat([data_sinus['Memory Length'],data_sinus['5000 ']], axis=1)
            data_sinus.columns = ['x','y']
            data_sinus['x'] = pd.to_numeric(data_sinus['x'],errors = 'coerce')
            data_sinus['y'] = pd.to_numeric(data_sinus['y'],errors = 'coerce')
        elif device == "Micsig":
            data_sinus = pd.concat([data_sinus['time'],data_sinus['Vol.']], axis=1)
            data_sinus.columns = ['x','y']
            
        new_list = data_sinus['y'].to_numpy()

        maxIndex = new_list[0:int(cycleMem)].argmax(axis=0)

        if maxIndex < quarter :
            arrIndex = np.arange(start=quarter-maxIndex, stop=allMem+quarter-maxIndex+1, step=1)
        else:
            arrIndex = np.arange(start=cycleMem+(quarter-maxIndex), stop=allMem+cycleMem+(quarter-maxIndex)+1, step=1)

        arrSine = np.array([])
        for element in arrIndex:
            if element % cycleMem == 0:
                arrSine = np.append(arrSine,360)
            else:
                arrSine = np.append(arrSine,((element % cycleMem)/cycleMem)*360)

        data_sensor = pd.read_csv("output/{}{}.csv".format(sens_name, x))
        if device == 'GWInstek':
            data_sensor = pd.concat([data_sensor['Memory Length'],data_sensor['5000 ']], axis=1)
            data_sensor = data_sensor.iloc[15:]
            data_sensor.columns = ['x','y']
            data_sensor['x'] = pd.to_numeric(data_sensor['x'],errors = 'coerce')
            data_sensor['y'] = pd.to_numeric(data_sensor['y'],errors = 'coerce')
        elif device == "Micsig":
            data_sensor = pd.concat([data_sensor['time'],data_sensor['Vol.']], axis=1)
            data_sensor.columns = ['x','y']

        arrSensor = data_sensor['y'].to_numpy()*1000

        type_sensor = []
        for element in arrSensor:
            type_sensor.append("sensor")

        df = pd.DataFrame((zip(arrSine,arrSensor.flatten(),type_sensor)),columns =['deg', 'voltage_mV', 'kind'])
        df = df[
            ((df['voltage_mV'] > bgn_pos) & (df['deg'] <= 180) & df['kind'].isin(['sensor'])) |
            ((df['voltage_mV'] < bgn_neg) & (df['deg'] >= 180) & df['kind'].isin(['sensor'])) |
            df['kind'].isin(['sine'])
        ]

        df = pd.concat([df1,df])
        df.reset_index(inplace=True, drop=True)
        

        # fig_mV.write_image("output/{}_pic_2d_mV.png".format(x))
        # fig_pC.write_image("output/{}_pic_2d_pC.png".format(x))
        # fig_3D_mV.write_image("output/{}_pic_3d_mV.png".format(x))
        # fig_3D_pC.write_image("output/{}_pic_3d_pC.png".format(x))

        # fig_2d_mV = fig_mV.to_image(format="jpeg")
        # fig_2d_mv_io = io.BytesIO(fig_2d_mV)

        if x == filecouple:
            # generate sine wave
            type_sine = []
            Fs = 360
            sample = 1000
            step = 360/sample
            sine_x = np.arange(start=0, stop=360, step=step)

            if dfFilterPos['voltage_mV'].max() > abs(dfFilterNeg['voltage_mV'].min()):
                max_sine = dfFilterPos['voltage_mV'].max() * 1.4
            else:
                max_sine = abs(dfFilterNeg['voltage_mV'].min()) * 1.4

            sine_y = max_sine * (np.sin(2*np.pi*sine_x/Fs))
            for element in sine_x:
                type_sine.append("sine")
            df1 = pd.DataFrame((zip(sine_x,sine_y,type_sine)),columns =['deg', 'voltage_mV', 'kind'])

            df = pd.concat([df1,df])
            df.reset_index(inplace=True, drop=True)

            # calibration state
            charge = df["voltage_mV"].tolist()
            for element in charge:
                if element > 0:
                    element = element * cal_m + cal_b
                else:
                    element = element * cal_m - cal_b

            df_charge = pd.DataFrame(charge, columns =['charge_pC'])
            df_charge.reset_index(inplace=True, drop=True)
            df = pd.concat([df, df_charge['charge_pC']], axis=1)
            print(df)
            
            count_series = df.groupby(['deg', 'voltage_mV', 'kind']).size()
            df3D_mV = count_series.to_frame(name = 'size').reset_index()
            fig_3D_mV = px.scatter_3d(df3D_mV, x="deg", y="voltage_mV", z="size", color="kind", color_discrete_sequence=["#FC6955", "#3283FE"], height=800, title="{} {} at {} cycles".format(voltage, project, x*cycle))
            fig_3D_mV.update_traces(marker_size=5)

            count_series = df.groupby(['deg', 'charge_pC', 'kind']).size()
            df3D_mV = count_series.to_frame(name = 'size').reset_index()
            fig_3D_pC = px.scatter_3d(df3D_mV, x="deg", y="charge_pC", z="size", color="kind", color_discrete_sequence=["#FC6955", "#3283FE"], height=800, title="{} {} at {} cycles".format(voltage, project, x*cycle))
            fig_3D_pC.update_traces(marker_size=5)

            dfFilter = df[((df['voltage_mV'] > bgn_pos) & (df['deg'] <= 180) & df['kind'].isin(['sensor']))]
            nPos = len(dfFilter)
            nPosCycle = round(nPos/(numCycle),2)

            dfFilter = df[((df['voltage_mV'] < bgn_neg) & (df['deg'] >= 180) & df['kind'].isin(['sensor']))]
            nNeg = len(dfFilter)
            nNegCycle = round(nNeg/(numCycle),2)

            fig_mV = px.scatter(df, x="deg", y="voltage_mV", color="kind", color_discrete_sequence=["#FC6955", "#3283FE"], height=800, title="{} {} at {} cycles".format(voltage, project, x*cycle))
            fig_mV.update_traces(marker_size=5)
            
            fig_pC = px.scatter(df, x="deg", y="charge_pC", color="kind", color_discrete_sequence=["#FC6955", "#3283FE"], height=800, title="{} {} at {} cycles".format(voltage, project, x*cycle))
            fig_pC.update_traces(marker_size=5)

            tab1, tab2, tab3, tab4 = st.tabs(["2D Voltage Unit", "2D Charge Unit", '3D Voltage Unit', '3D Charge Unit'])
            with tab1:
                st.plotly_chart(fig_mV, use_container_width=True)
            with tab2:
                st.plotly_chart(fig_pC, use_container_width=True)
            with tab3:
                st.plotly_chart(fig_3D_mV, use_container_width=True)
            with tab4:
                st.plotly_chart(fig_3D_pC, use_container_width=True)

            print("cycle: ",x*cycle)
            print("nPos: ", nPos)
            print("nNeg: ", nNeg)
            print("nPosCyc: ", nPosCycle)
            print("nNegCyc: ", nNegCycle)
            dfFilterPos = df[((df['voltage_mV'] > 0) & df['kind'].isin(['sensor']))]
            print("topPos: ", dfFilterPos['voltage_mV'].max())
            print("strDegPos: ", dfFilterPos['deg'].min())
            print("endDegPos: ", dfFilterPos['deg'].max())
            print("kurtPos: ", dfFilterPos['voltage_mV'].kurt())
            print("skewPos: ", dfFilterPos['voltage_mV'].skew())
            dfFilterNeg = df[((df['voltage_mV'] < 0) & df['kind'].isin(['sensor']))]
            print("topNeg: ", dfFilterNeg['voltage_mV'].min())
            print("strDegNeg: ", dfFilterNeg['deg'].min())
            print("endDegNeg: ", dfFilterNeg['deg'].max())
            print("kurtNeg: ", dfFilterNeg['voltage_mV'].kurt())
            print("skewNeg: ", dfFilterNeg['voltage_mV'].skew())

            fields = ['parameter', 'value', 'unit']     
            rows = [
                    ['voltage', voltage, 'kV'], 
                    ['project', project, ''], 
                    ['cyle', x, 'unit'], 
                    
                    ['n_pos', nPos, 'unit'],
                    ['n_pos_cyc', nPosCycle, 'n/cycle'],
                    ['top_pos', dfFilterPos['voltage_mV'].max(), 'volt'],
                    ['str_deg_pos', dfFilterPos['deg'].min(), 'deg'],
                    ['end_deg_pos', dfFilterPos['deg'].max(), 'deg'],
                    ['kurt_pos', dfFilterPos['voltage_mV'].kurt(), 'unit'],
                    ['skew_pos', dfFilterPos['voltage_mV'].skew(), 'unit'],
                    
                    ['n_neg', nNeg, 'unit'],
                    ['n_neg_cyc', nNegCycle, 'n/cycle'],
                    ['top_neg', dfFilterNeg['voltage_mV'].min(), 'volt'],
                    ['str_deg_neg', dfFilterNeg['deg'].min(), 'deg'],
                    ['end_deg_neg', dfFilterNeg['deg'].max(), 'deg'],
                    ['kurt_neg', dfFilterNeg['voltage_mV'].kurt(), 'unit'],
                    ['skew_neg', dfFilterNeg['voltage_mV'].skew(), 'unit']
                ]
            
            csv = df.to_csv(index=False)
            csv_bytes = csv.encode()
            csv_io = io.BytesIO(csv_bytes)

            # filename = "output/0_recap.csv"
            # with open(filename, 'w') as csvfile:
            #     csvwriter = csv.writer(csvfile)
            #     csvwriter.writerow(fields)
            #     csvwriter.writerows(rows)
            # show_df = st.dataframe(pd.read_csv(filename))
            
            
            # shutil.make_archive('proty', 'zip', 'output')
            # folder = 'output/'
            # for filename in os.listdir(folder):
            #     file_path = os.path.join(folder, filename)
            #     try:
            #         if os.path.isfile(file_path) or os.path.islink(file_path):
            #             os.unlink(file_path)
            #         elif os.path.isdir(file_path):
            #             shutil.rmtree(file_path)
            #     except Exception as e:
            #         print('Failed to delete %s. Reason: %s' % (file_path, e))

        # df = df.drop('charge_pC', axis=1)
        df1 = df

def main():
    global voltage,project,device,filecouple,cycle,bgn_pos,bgn_neg,cal_m,cal_b,dl_image,show_image,sine_name,sens_name,my_bar
    st.set_page_config(layout="wide")

    left_co1, left_co2, cent_co,last_co, last_co1 = st.columns(5)
    with cent_co:
        image = Image.open('asset/logo.png')
        st.image(image)
    
    st.title('Phase Pattern :blue[Partial Discharge] Generator ')
    placeholder = st.empty()
    with placeholder.form("regis_form", clear_on_submit=False):
        
        cols = st.columns(5)
        voltage = cols[0].number_input('Working voltage (kV)', step=0.5)
        project = cols[1].text_input('Project name')
        device = cols[2].selectbox('Device used', ('GWInstek', 'Micsig'))
        filecouple = cols[3].number_input('Filecouple', step=1)
        cycle = cols[4].number_input('Cycle per file', step=1)

        cols = st.columns(4)
        bgn_pos = cols[0].number_input('Bgn positive (mV)')
        bgn_neg = cols[1].number_input('Bgn negative (mV)')
        cal_m = cols[2].number_input('y=mx+b (m)')
        cal_b = cols[3].number_input('y=mx+b (b)')

        cols = st.columns(3)
        static_store = get_static_store()
        uploaded_files = cols[0].file_uploader("Upload .zip file", accept_multiple_files=True)
        if len(uploaded_files) > 0:
            for file in uploaded_files:
                if file.type == "application/zip":
                    with ZipFile(file, "r") as z:
                        z.extractall(path='output/')

        sine_name = cols[1].text_input('Sine filename, ex: filename(n).csv', 'sine')
        sens_name = cols[2].text_input('Sensor filename, ex: filename(n).csv', 'sens')

        my_bar = st.progress(0)
        submitted = st.form_submit_button("Submit")
        if submitted:
            app()
    
    # if submitted:
    #     with open('proty.zip', 'rb') as f:
    #         st.download_button('Download Zip', f, file_name='proty.zip')


if __name__ == "__main__":
    main()