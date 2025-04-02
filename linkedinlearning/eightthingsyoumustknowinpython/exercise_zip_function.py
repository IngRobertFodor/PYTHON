years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
births = [723_165, 723_913, 729_674, 698_512, 695_233, 697_852, 696_271, 679_106, 657_076, 640_370]

def annual_births_average(year=years, births=births):
   '''Return a list of tuples with each entry in this format
      (year, birth, running_average)
      Round the running_average to the nearest integer. 
   ''' 
   r_a = []
   running_average = []
   for i in range(len(years)):
      r_a.append(births[i])
      x = sum(r_a)/len(r_a)
      running_average.append(round(x))
   #print(r_a)
   #print(running_average)

   my_full_tupleslist = list(zip(years, births, running_average))
    
   return my_full_tupleslist


print(annual_births_average())