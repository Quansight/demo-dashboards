from data_ingest import austin_trees
import panel as pn

pn.extension()

def plot():
    object = austin_trees()
    dataset_raw = object.pre_processing()
    dataset_processed = object.geo_plot_ready_data(dataset_raw)
    component_map = object.geo_plot(dataset_processed)
    component_violin = object.violin_plot(dataset_raw)
    component_dist = object.distribution_plot(dataset_raw)
    component_specie_diversity = object.diversity_trees_plot(dataset_raw)
    plot_component = pn.Row(pn.Column(component_map, component_violin, 
                                      component_dist, component_specie_diversity))
    view = pn.template.FastListTemplate(
           site="Austin trees 🌴🌱", 
           title="Specie info and more", 
           main=[plot_component]
           )
    return view 


if __name__ == "__main__":
    pn.serve(
        plot,
        port=5006,
        websocket_origin=['*'],
        autoreload=True,
        start=True,
        location=True,
        )
    