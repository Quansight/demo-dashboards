from data_ingest import austin_trees
import panel as pn

pn.extension()


def plot():
    object = austin_trees()
    dataset_raw = object.pre_processing()
    dataset_processed = object.geo_plot_ready_data(dataset_raw)
    component = object.geo_plot(dataset_processed)
    return component


if __name__ == "__main__":
    pn.serve(
        plot,
        port=5006,
        websocket_origin=['*'],
        autoreload=True,
        start=True,
        location=True,
        )