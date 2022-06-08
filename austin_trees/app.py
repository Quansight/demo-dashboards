from data_ingest import austin_trees
import panel as pn
import argparse

pn.extension()


def plot_page():
    object = austin_trees()
    dataset_raw = object.pre_processing()
    dataset_processed = object.geo_plot_ready_data(dataset_raw)
    component = obj.geo_plot(dataset_processed)
    return component.view()

def homepage():
    print("homepage", flush=True)
    return pn.panel(pn.pane.Markdown("# Homepage"))

if __name__ == "__main__":
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
    pn.serve({  
            '/':homepage,
            '/austin_trees': plot_page 
        },
            
        title={
            '/': 'home',
            '/austin_trees' : 'Austin trees'
        },
        websocket_origin=[args.address],
        autoreload=True,
        start=True,
        location=True,
        port=int(args.port),

        )