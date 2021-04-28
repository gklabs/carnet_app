import pandas as pd
import numpy as np
from scipy.stats import truncnorm
import random
import copy
import math
import gurobipy as gp
from gurobipy import GRB
import timeit

start = timeit.default_timer()

random.seed(42)
class vehicle:
    def __init__(self,eq_no,eq_desc,vtype,dept,dept_id, purchasedate,age2020,current_age,purchaseprice,depreciated2020,miles2020,vmt2020,mandr2020,cumulativemandr2020,totcum_mandr, mpg2020,emission2020, vmt, replacementvehicle_id, replacement_vehicle_desc,replacement_vehicle_purchaseprice,replacement_vehicle_mpge,replacement_vehicle_type,decision):
        self.eq_no = eq_no
        self.eq_desc = eq_desc
        self.age2020= age2020
        self.current_age= current_age
        self.purchaseprice= purchaseprice
        self.dept= dept
        self.deptid = dept_id

        
        self.miles2020= miles2020
        self.mpg2020= mpg2020
        self.vmt2020 = vmt2020
        self.vmt=vmt
        self.mandr2020= mandr2020
        self.cumulativemandr= cumulativemandr2020
        self.depreceated2020= depreciated2020
        self.vtype= vtype
        
        
        self.replacementvehicle_id = replacementvehicle_id
        self.replacement_vehicle_desc = replacement_vehicle_desc
        self.replacement_vehicle_purchaseprice=replacement_vehicle_purchaseprice
        self.replacement_vehicle_mpge = replacement_vehicle_mpge	
        self.replacement_vehicle_type=  replacement_vehicle_type  
        
        self.ypd = 0
        self.decision= decision
        self.last_replaced_year = self.purchase_year  
        self.valuefunc = {}
        self.replacement_schedule = []

    @property
    def purchase_year(self):
        try:
            p_year = int(2020- self.age2020)
            return p_year
        except:
            print("cant compute purchase year")


    @property
    def life_years(self):
        
        start = self.purchase_year
        
        end = UI_params['end_year']

        try:
            life_years= [item for item in range(start,end+1)]
            return life_years
        except:
            print("cant compute life years")
            


    @property
    def annualmiles(self):
        miles_dict= {}
        #Assigning same miles for all the years in the planning horizon
        for t in self.life_years:
            miles_dict[t]= self.miles2020
        return miles_dict
    
    @property
    def mpg(self):
        mpg_dict= {}
        option= "deterioration"
        computedmpg= self.mpg2020
        
        if option == "constant":
            det_factor=1
            build_factor =1
        #assumes a 10% deterioration rate every year
        elif option == "deterioration":
            det_factor = 0.95
            build_factor = 1.02
        
        currentyear_index = self.life_years.index(2020)

        for t in range(currentyear_index,-1):
            mpg_dict[life_years[t]]= computedmpg * build_factor

        for t in self.life_years:
            if t>2020:
                computedmpg= computedmpg* det_factor
            
            mpg_dict[t]= computedmpg
        
        return mpg_dict

    ##TODO-read fuel cost from csv file.
    @property
    def fuel(self):
        
        fuel_dict={}
        option = "constant"

        if option == "random":
        #truncated normal distribution for fuel price per gallon
            lower, upper= 2,3
            mu,sigma= 2.35,0.05
            f_x= truncnorm((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)
            f_p= f_x.rvs(len(self.life_years))
        
        elif option == "constant":
            f_p= np.repeat(2.35,len(self.life_years))
            f_mpge = np.repeat(1.16,len(self.life_years))
        
        if self.vtype == "ICE":
            for index,t in enumerate(self.life_years):
                if (t<= self.age2020):
                    fuel_dict[t]= self.annualmiles[t]/self.mpg[t] * f_p[index]
                else:
                    fuel_dict[t]= self.annualmiles[t]/self.mpg[t] * f_p[index]
        else:
            for index,t in enumerate(self.life_years):
                if (t<= self.age2020):
                    fuel_dict[t]= self.annualmiles[t]/self.mpg[t] * f_mpge[index]
                else:
                    fuel_dict[t]= self.annualmiles[t]/self.mpg[t] * f_mpge[index]
        return fuel_dict

    @property
    def mandr(self):
        option= "constant"
        mandr_dict= {}
        vmt= self.vmt
        computedmandr= self.mandr2020
      
        
        for t in self.life_years:
            if (t<= 2020):
                computedmandr = self.cumulativemandr/(self.age2020+1)
            else:
                vmt= vmt+self.annualmiles[t]
                if vmt <= 10000:
                    factor = 1
                elif 10000<vmt<=150000 :
                    factor = 1.05
                else:
                    factor= 1.15
                
                computedmandr= computedmandr *factor
            
            mandr_dict[t]= computedmandr 
        return mandr_dict

    @property
    def purchase(self):
        purchase_dict={}
        computedpp= self.replacement_vehicle_purchaseprice

        for t in self.life_years:
            
            if t<= 2020:
                computedpp= self.purchaseprice
            else:
                 computedpp= self.purchaseprice

            purchase_dict[t] = computedpp
        return purchase_dict
    
    @property
    def emission(self):
        emission_dict ={}
        if self.vtype == "ICE":            
            for t in self.life_years:
                fuel_consumed = self.annualmiles[t]/self.mpg[t]
                emission_dict[t]= fuel_consumed * carbon_factor
        else:
            for t in self.life_years:
                fuel_consumed = self.annualmiles[t]/self.mpg[t] *0.5
                emission_dict[t]= fuel_consumed * carbon_factor

        
        return emission_dict
        

    @property
    def depreciation(self):
        age= self.current_age
        
        cur_depvalue = self.depreceated2020
        cur_depvalue2 = self.purchaseprice
        
        depreciation_dict={}
        
        amt_depreceated = self.purchaseprice - self.depreceated2020
        
        # print(self.purchaseprice, self.depreceated2020,amt_depreceated)

        for t in self.life_years:
            
            if t>2020:
                if 0<= age <=1:
                    cur_depvalue = cur_depvalue - 0.25*cur_depvalue
                    
                elif age >=2:
                    cur_depvalue = cur_depvalue - 0.12*cur_depvalue
                
                depreciation_dict[t] = cur_depvalue
                    
            else:
                cur_depvalue2 = cur_depvalue2 - amt_depreceated/(self.age2020+1)
            
                depreciation_dict[t] = cur_depvalue2    
            age+=1
        
        return depreciation_dict
    

class portfolio:
    def __init__(self,t,totfuelcost,totmandrcost,amt_spent,totemission,percent_decrease,v_count,n_replaced):
        self.t= t
        # self.portfolio= vset
        self.totfuelcost= totfuelcost
        self.totmandrcost= totmandrcost
        self.amt_spent = amt_spent
        self.totemission= totemission
        self.percent_decrease= percent_decrease
        self.v_count = v_count
        self.n_replaced= n_replaced



# decides whether to keep or replace a given vehicle based on intrinsic numbers without the budget in mind
class dynamic_prog:
    def replace(self,v,x):

        #change mpg with EV characteristics
        mpg_dict ={}
        computedmpg= v.replacement_vehicle_mpge 
        factor = 0.98
        for i in range(x,interval):
            computedmpg= computedmpg* factor
            mpg_dict[i]= computedmpg
        

        for i in range(x,len(v.mpg)):
            v.mpg[i]= mpg_dict[i]
        
        #change Fuel costs
        fuel_dict = {}
        option= "constant"
        if option == "random":
            pass
        elif option == "constant":
            f_p= np.repeat(2.1, len(range(x,interval)))
        
        for i in range(x,interval):
            fuel_dict[i]= v.annualmiles[t]/v.mpg[t] * f_p[i]
        
        for i in range(x,len(v.fuel)):
            v.fuel[i]= fuel_dict[i]
    

        #change mandr costs
        mandr_dict = {}

        #change emission costs 
        for i in range(x,len(v.emission)):
            v.emission[x]= 0

        
    def oldcontributionfunction(self,v,t):
        decision= 'keep'
        #compute contribution function
        # the cost of holding the vehicle from year 't' to year 'x'
        C_x = {}
        
        #initialize all the costs to zero
        P_t= 0
        M_t= 0
        E_t = 0
        F_t = 0
        g_x= {}
        M_t_future =0
        E_t_future=0
        F_t_future=0
        sale_year={}
        
        #--- Current year costs ---- #
        for x in range(t+1,interval):
            
            # purchase cost adjusted with depreciation
            P_t = v.replacement_vehicle_purchaseprice - v.depreciation[x]
            
            for i in range(t,x):
                M_t = M_t+ v.mandr[i]
                E_t= E_t+ (v.emission[i] * emission_to_dollar)
                F_t = F_t+ v.fuel[i]
                current_costs = (M_t,E_t,F_t)

            for j in range(x+1,interval):
                temp_v= copy.copy(v)
                replace(temp_v,x)
                M_t_future = M_t_future+ temp_v.mandr[j]
                E_t_future= E_t_future+ (temp_v.emission[j] * emission_to_dollar)
                F_t_future = F_t_future+ temp_v.fuel[j]


   

            C_x[x] = M_t + E_t+ F_t + P_t
            g_x[x]= M_t_future + E_t_future + F_t_future

        # print("C_x:",C_x)
        # print("g_x:",g_x)
        
        arg_min= 1
        min_cost = C_x[1] + g_x[1]
        min_costs_portfolio =[]
        arg_min_portfolio=[]
        for x in range(2,len(C_x)):
            
            temp = C_x[x]+g_x[x]
            if temp < min_cost:
                min_cost = temp
                arg_min = x
        
        min_costs_portfolio.append(min_cost)
        arg_min_portfolio.append(arg_min)
        # print("min_cost:",min_cost,"arg_min:",arg_min)
        print(arg_min_portfolio)


        # g_t[interval]= 100000
        # g_t[interval-1]= C_tx[(interval-1,interval)]
        # # ----- Future years costs ---- #
        # for i in range(interval-2,t,-1):
        #     temp_g={}
        #     for x in range(interval,i+1,-1):
        #         # print(i,x)
        #         temp_g[x]= C_tx[(i,x)]+g_t[x]
            
        #     g_t[i] = min(temp_g.values())

        #     sale_year[i] = min(temp_g,key=temp_g.get)

        # print("g_t:",g_t,"\nsaleyear:",sale_year)
       
        decision= {}
        return decision


    def contributionfunction(self,v):
        regeneration_value = {}

        horizon = len(v.life_years)
        # print("horizon:",horizon," years")
        for index,t in enumerate(v.life_years):
            other_costs=0
            for j in range(index):
                other_costs = other_costs + v.mandr[v.life_years[j]] + v.fuel[v.life_years[j]] + v.emission[v.life_years[j]]

            regeneration_value[t]= v.purchase[t] - v.depreciation[t] + other_costs
        
        min_value = []
        min_index=[]
        fut_value = 1000
        
        #value iteration
        x = [fut_value]*horizon
        zeros= [0]*horizon
        f= np.vstack((zeros,[x]))        
        min_value.append(min(f[1]))
        min_index.append(1)
        beta = 0.98
        flag=0
        j=1
        epsilon = 0.01 
        # print(f)
        # print(regeneration_value)

        while flag!=1:
            y=[]
            for index,item in enumerate(v.life_years[:horizon]):
                cell = (beta**(index+1))* f[j][index] + regeneration_value[item]
                y.append(cell)
                
            # print(y)
            # print(min(y))
            min_value.append(min(y))
            min_index.append(y.index(min(y)))
            f= np.vstack((f,y))
            

            if min_value[j]-min_value[j-1] < epsilon:
                flag=1

            j+=1

        replacement_year= v.life_years[min_index[j-1]]
        # print(j)
        # print(v.life_years[min_index[j-1]])
        # print(min_index)

        # print("done")
        return replacement_year
        
        

### Read data
input_path_mac = "/Users/gkbytes/carnet_app/DP/"
input_path_windows= r"C:\Users\girid\Documents\carnet_app\DP"

vehicle_info= pd.read_csv(input_path_mac+r"vehicle_info_prefinal.csv",thousands=r',')
# print(vehicle_info.head(10))
# print(vehicle_info.shape)
replacement_vehicle_info= pd.read_csv(input_path_mac+r"replacement_vehicle_info.csv", thousands=r',')

vportfolio=[]
replacement_fleet = []
emission_to_dollar = 120
carbon_factor = 2.412

def read_info(vehicle_info):
    colnames= list(vehicle_info.columns.values)
    vportfolio = []
    for index,row in vehicle_info.iterrows():
        if pd.isnull(row['equipmentid'])== False:
            eq_no= row['equipmentid']
            eq_desc= row['vehicledescription']
            vtype = row['vehicle_type']
            dept= row['dept_name']
            dept_id =row['deptid']
            purchasedate= row['purchasedate']
            age2020= row['age2020']
            current_age = age2020
            purchaseprice= row['purchaseprice']
            depreciated2020 = row['depreceated value']
            miles2020= row['miles2020']
            vmt2020= row['cumulative_miles']
            mandr2020= row['maintenance2020']
            cumulativemandr2020= row['cumulative_maintenance']
            totcum_mandr = cumulativemandr2020
            mpg2020= row['mpg2020']
            emission2020= row['emissions2020']
            vmt= vmt2020
            replacementvehicle_id = row['replacementvehicle_id']
            replacement_vehicle_desc = row['replacement_vehicle_desc']
            replacement_vehicle_purchaseprice = row['replacement_vehicle_purchaseprice']
            replacement_vehicle_mpge = row['replacement_vehicle_mpge']		
            replacement_vehicle_type= row['replacement_vehicle_type']   
            decision = 0
            
            
            v= vehicle(eq_no,eq_desc,vtype,dept,dept_id, purchasedate,age2020,current_age,purchaseprice,depreciated2020,miles2020,vmt2020,mandr2020,cumulativemandr2020,totcum_mandr, mpg2020,emission2020, vmt, replacementvehicle_id, replacement_vehicle_desc,replacement_vehicle_purchaseprice,replacement_vehicle_mpge,replacement_vehicle_type,decision)
            
            vportfolio.append(v)
    return vportfolio

# reading existing vehicle and replacement vehicle information
vportfolio = read_info(vehicle_info)
replacement_fleet = read_info(replacement_vehicle_info)

## enter input
UI_params = {
    'initial_procurement_budget':5000000,
    'procurement_budget_growthrate':0.03,
    'start_year':2021,
    'end_year':2037,
    'emissions_target_pct_of_base':0.40,
    
    # 'min_miles_replacement_threshold':150000,#miles
    # 'max_vehicles_per_station':1000
    # 'objective_weights':{'cost':0.01,'emissions':0.99},
    # 'emissions_baseline': 1000,#metric tons
    # 'min_vehicle_age_replacement_threshold':60,#years
    # 'initial_maintenance_budget':1000000,
    # 'maintenance_budget_rate':0.03,
}

print(len(vportfolio))
interval =  UI_params['end_year']- UI_params['start_year']
projected_years = [item for item in range(UI_params['start_year'], UI_params['end_year']+1)]
budget= {}
for idx,year in enumerate(projected_years):
    budget[year] = UI_params['initial_procurement_budget'] * (1+ UI_params['procurement_budget_growthrate'])**float(idx)

BC_vehicle_fleet = []
def create_fleet_stat(vportfolio,amt_spent,t, n_replaced):
    totfuelcost=0
    totmandrcost=0
    totemission=0
    v_count = {"HEV":0,"PHEV":0, "ICE":0}
    for v in vportfolio:
        totfuelcost = totfuelcost + v.fuel[t]
        totmandrcost = totmandrcost + v.mandr[t]
        totemission = totemission + v.emission[t]
        
        if v.vtype == "HEV":
            v_count['HEV']+= 1
        elif v.vtype == "PHEV":
            v_count['PHEV']+=1
        else:
            v_count['ICE']+= 1 

    if t!= UI_params['start_year']:
        percent_decrease= (BC_vehicle_fleet[0].totemission -totemission)/BC_vehicle_fleet[0].totemission
    else:
        percent_decrease =0
    p= portfolio(t,totfuelcost,totmandrcost,amt_spent,totemission,percent_decrease,v_count,n_replaced)
   
    BC_vehicle_fleet.append(p)

def normalised(x,minimum,maximum):
    normalised_x = (x-minimum)/(maximum - minimum)
    return normalised_x

def rev_normalised(x,minimum,maximum):
    if x== minimum and x== maximum:
        return x
    else:
        revnormalised_x = (x-maximum)/(minimum - maximum)
    return revnormalised_x

def modify_fleet(items,curr_fleet,t):
    pur_date = "12/31/" + str(t)
    init_len = len(curr_fleet)
    print("fleet size:",init_len)
    added_fleet= []
    removed_fleet = []
    replacement_found=0
    for i in items:
        for v in curr_fleet:
            if i == v.eq_no:
                if "R" in str(i):
                    v.vmt = 0
                    v.purchasedate = pur_date
                else:
                    replacement_id = v.replacementvehicle_id
                    for ov in replacement_fleet:
                        if ov.eq_no == replacement_id:
                            replacement_found =1
                            ov.purchasedate = pur_date
                            added_fleet.append(ov)
                            # print(ov.vtype)
                    removed_fleet.append(v)
                    curr_fleet.remove(v)
    
    newfleet= curr_fleet + added_fleet
    if len(newfleet) == init_len:
        print("vehicle replaced successfully",t)
        print("======================================")
    else:
        print("replacement unsuccsessful")
    return newfleet


def main():
    print("interval:",interval+1)
    eligiblevehicles=[]
    
    count=0
    
    ########## First Stage model ##########
    for v in vportfolio:
        #start DP calculations
        dp_optimizer= dynamic_prog()
        if math.isnan(v.eq_no)==False:
            # print(v.eq_no, v.eq_desc)
            v.decision = dp_optimizer.contributionfunction(v)
            count+=1
    
    count_rep = 0
    for v in replacement_fleet:
        #start DP calculations
        dp_optimizer= dynamic_prog()
        # if math.isnan(v.eq_no)==False:
            # print(v.eq_no, v.eq_desc)
        v.decision = dp_optimizer.contributionfunction(v)
        count_rep+=1  
        
    print("count:",count)
    print("count_rep:",count_rep)
    print("Stage 1 completed")
    stop1 = timeit.default_timer()

    print('Time: ', stop1 - start)  
    
    
    ############ Second Stage model ###############
    values=[]
         
    for v in vportfolio:
        v.ypd= v.decision- UI_params['start_year']
    
    create_fleet_stat(vportfolio,0,UI_params['start_year'],0)

    current_fleet = vportfolio.copy()
    selected = {}
    
    
    for t in projected_years:
        amt_spent=0
        #normalization
        replace_queue=[]
        min_age = min([v.current_age for v in current_fleet])
        max_age = max([v.current_age for v in current_fleet])

        min_vmt = min([v.vmt for v in current_fleet])
        max_vmt = max([v.vmt for v in current_fleet])

        min_ypd = min([v.ypd for v in current_fleet])
        max_ypd = max([v.ypd for v in current_fleet])

        min_emission = min([v.emission[t] for v in current_fleet])
        max_emission = max([v.emission[t] for v in current_fleet])
        #for simplicity, we assume that all vehicles are replaced on Dec 31 of every year

        w_currage = 0.25
        w_vmt = 0.25
        w_ypd = 0.25
        w_emission = 0.25
        for v in current_fleet:
            
            v.valuefunc[t]= w_currage* normalised(v.current_age,min_age,max_age) + w_vmt* normalised(v.vmt,min_vmt,max_vmt) + w_ypd* rev_normalised(v.ypd,min_ypd,max_ypd) + w_emission * normalised(v.emission[t], min_emission, max_emission)
            temp= [t,v.eq_no,v.eq_desc,v.decision,v.current_age, v.vmt,v.ypd,v.valuefunc]
            values.append(temp)

        eq_nos = [v.eq_no for v in current_fleet]
        score= [v.valuefunc[t] for v in current_fleet]
        prices = [v.replacement_vehicle_purchaseprice for v in current_fleet]
        n= len(current_fleet)
        print("N:",n)

        try:
            m = gp.Model("year_model")
            #create variables
            x={}
            x = m.addVars(n,vtype = GRB.BINARY, name= "v")
            budg_constr = m.addConstr(gp.quicksum( prices[i] * x[i] for i in range(n)) <= budget[t], "budget_constr")

            expr= gp.quicksum(score[i]* x[i] for i in range(n))
            m.setObjective(expr,GRB.MAXIMIZE)
            m.optimize()
            
            items =[]
            for i in range(n):
                if x[i].X > 0.5:
                    items.append(eq_nos[i])
                    amt_spent = amt_spent+ prices[i]
                    
            selected[t] = items
            print("=====================================================")
            print("amt_spent in year",t,"is:", amt_spent)
            print("=====================================================")
        except gp.GurobiError as e:
            print('Error code ' + str(e.errno) + ': ' + str(e))
        
        except AttributeError:
            print('Encountered an attribute error')
        
        #get fleet statistics
        create_fleet_stat(current_fleet,amt_spent,t,len(items))
        #replace the selected vehicles with EVs
        current_fleet = modify_fleet(items, current_fleet,t)
        #updating age and vmt after completion of year   
        for v in current_fleet:
            v.current_age+=1
            v.vmt= v.vmt+ v.annualmiles[t]
    
    # temp_output = pd.DataFrame(values,columns= ["t","no","desc","decision","age","vmt","ypd","value"]).reset_index(drop=True)
    # temp_output.to_csv("temp_output.csv")
    f= open(r"C:\\Users\\girid\\Documents\\carnet_app\\DP\\metrics.txt",'w+')
    # print year-wise status
    for status in BC_vehicle_fleet:
        print("=======================")
        print("t:",status.t)
        print("Emission:",status.totemission)
        print("decrease %:",status.percent_decrease)
        print("AmtSpent:",status.amt_spent)
        print("Budget:",budget[status.t], "Utilization:",amt_spent/budget[status.t])
        print("Count:",status.v_count)
        print("Number of vehicles replaced:",status.n_replaced)
        print("=========================")

        print("=======================",file=f)
        print("t:",status.t,file=f)
        print("Emission:",status.totemission,file=f)
        print("decrease %:",status.percent_decrease,file=f)
        print("AmtSpent:",status.amt_spent,file=f)
        print("Budget:",budget[status.t], "Utilization:",amt_spent/budget[status.t],file=f)
        print("Count:",status.v_count,file=f)
        print("Number of vehicles replaced:",status.n_replaced, file=f)
        print("=========================")


    stop2 = timeit.default_timer()
    print('Time: ', stop2 - start)
    
    stat_df = pd.DataFrame([x.__dict__ for x in BC_vehicle_fleet])
    stat_file_name= "stats_"+str(UI_params['initial_procurement_budget'])
    stat_df.to_csv(input_path_mac+stat_file_name+".csv")

    selected_df =pd.DataFrame(list(selected.items()),columns = ['year','vehicles_replaced'])
    selected_df.to_csv(input_path_mac+"selected_vehicles"+str(UI_params['initial_procurement_budget'])+".csv")

            
                            
if __name__ == "__main__":
    main()



    