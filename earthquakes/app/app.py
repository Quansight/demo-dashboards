import panel as pn
from earthquakes_app import EarthquakesApp, get_earthquakes_df
import argparse

pn.extension()

earthquakes_df = None


def earthquakes_page(**kwargs):
    
    print("earthquakes page", flush=True)

    lang_id = None
    if 'lg' in pn.state.session_args.keys():
        try:
            lang_id = pn.state.session_args.get('lg')[0].decode('utf-8')
        except:
            pass

    component = EarthquakesApp(lang_id=lang_id, df=earthquakes_df)
    return component.view()


def homepage():
    print("homepage", flush=True)
    return pn.panel(pn.pane.Markdown("# Homepage"))


if __name__ == "__main__":

    """
    Pierre - Update 2022 05 14 :
    To make it run, we need to have a panel-serve framework in CDSDashboards.
    
    """

    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--address",
        required=True,
        help="Address on which the Panel app is served",
    )
    parser.add_argument(
        "-p",
        "--port",
        required=True,
        help="Port on which the Panel app is served",
    )
    parser.add_argument(
        "-m",
        "--mode",
        required=False,
        default="dashboard",
        choices=["proxy", "dashboard"],
        help="""Mode of running this panel app :
        - 'proxy' if ran from the command line and accessed from the Proxy
        - 'dashboard' if ran by CDSDashboards and accessed by its given URL
        """,
    )
    args = parser.parse_args()

    print("loading earthquakes data")    
    earthquakes_df = get_earthquakes_df()

    
    pn.serve({  
                '/':homepage,
                '/earthquakes': earthquakes_page 
            },
             
            title={
                '/': 'home',
                '/earthquakes' : 'Earthquakes'
            },

            websocket_origin=[args.address],
            autoreload=True,
            start=True,
            location=True,
            port=int(args.port),

            #threaded=True,
            # check_unused_sessions=3,
            # unused_session_lifetime=3
    )
