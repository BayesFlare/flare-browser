import web
import matplotlib
import matplotlib.pyplot as pl
import numpy as np
import bayesflare as bf
import pylightcurve as lc
import pyscidata
import pyscidata.solar
import pyscidata.solar.goes
import cStringIO
import vincent

web.config.debug = True
render = web.template.render('templates/')

urls = (
  '/', 'index',
  '/lightcurve/(.+)/(.+)', 'Lightcurve',
  '/list/(.+)/(.+)', 'list',
    '/flare/(.+)', 'flare'
)


class index:
    
  def GET(self):
      return render.index()

class Lightcurve:
    def plot(self, start, end):
        data = pyscidata.solar.goes.GOESLightcurve(start, end, \
                                               title='GOES', default='xrsb', cadence='1min')

        listing = bf.Flare_List('flare.db')
        tags = listing.flare_dataframe(start = start, end = end)
        data = data.import_tags(tags, 'bayesflare')
        fig, ax = pl.subplots(1,1,figsize=(13,4), frameon=False, dpi=300)
        ax.patch.set_visible(False)
        ax.set_yticks((1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2))
        ax.set_yticklabels(('', 'A', 'B', 'C', 'M', 'X', ''))
        #ax.tick_params(axis='y', colors='green')
        #ax.patch.set_visible(False)
        ax.set_ylabel('1.0--8.0 $\AA$  [Watts m$^-2$]')
        ax.set_xlabel('Time')
        ax.set_yscale('log')
        ax.plot(data.data.index, data.data.xrsa, color='#049cdb')
        ax.set_ylim(1e-9, 1e-5)
        pl.setp( ax.xaxis.get_majorticklabels() )
        ymin, ymax = ax.get_ybound()
        xmin, xmax = ax.get_xbound()
        
        ax1 = ax.twinx()
        ax1.patch.set_visible(False)
        ax1.set_yscale('log')
        ax1.set_ylim(1e-9, 1e-5)
        #ax1.set_ylim(9e-7, 1e-6)
        #ax1.set_ylabel('1.0--8.0 $\AA$ | Watts m$^-2$')
        ax1.set_yticks(())
        #ax1.set_ylabel('0.5--4.0 $\AA$ | Watts m$^-2$')
        ax1.plot(data.data.index, data.data.xrsb, alpha=1, color='#9d261d')

        ax2 = ax.twinx()#.twiny()



        spines_to_remove = ['top', 'right']
        for spine in spines_to_remove:
            ax.spines[spine].set_visible(False)
        almost_black = '#262626'
        spines_to_keep = ['bottom', 'left']
        for spine in spines_to_keep:
            ax.spines[spine].set_linewidth(0.5)
            ax.spines[spine].set_color(almost_black)    
        #ax.grid(True)
        ax.yaxis.grid(True, which="major", linestyle='-', color=almost_black, linewidth=0.15)
        
        if data.tags:
          data.plot_tags(ax, 'model_peak_time', 'id', tags='bayesflare')
        
        format = "svg"
        sio = cStringIO.StringIO()
        pl.savefig(sio, format=format)
        print "Content-Type: image/%s\n" % format
        #msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY) # Needed this on windows, IIS
      
        return """<img width="100%" style="max-width: 1000px" src="data:image/svg+xml;base64,"""+sio.getvalue().encode("base64").strip()+""" "/>"""
        
    def GET(self, start, end):
      #start = '2014-03-01 00:00'
      #end = '2014-03-03 00:00'
      #print start, end
      return render.lightcurve(self.plot, start, end)

class id:
  def GET(self, id):
    id = str(id)
    list = bf.Flare_List('flare.db')
    table = list.id_select(id=id)
    flare_list = []
    for row in table:
        flare = list.dict_factory(row)
        flare['data_peak_amplitude'] = list.goes_class(flare['data_peak_amplitude'])
        flare['model_peak_amplitude'] = list.goes_class(flare['model_peak_amplitude'])
        flare_list.append(flare)
    return render.flare(flare_list)

class list:
  def GET(self, start, end):
    start = str(start)
    end = str(end)
    list = bf.Flare_List('flare.db')
    table = list.flare_select(start=start, end=end)
    flare_list = []
    for row in table:
        flare = list.dict_factory(row)
        flare['data_peak_amplitude'] = list.goes_class(flare['data_peak_amplitude'])
        flare['model_peak_amplitude'] = list.goes_class(flare['model_peak_amplitude'])
        flare_list.append(flare)
    return render.list(flare_list)
    

if __name__ == "__main__": 
    app = web.application(urls, globals())
    app.run()     