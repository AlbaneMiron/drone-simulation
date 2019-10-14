# AUTO GENERATED FILE - DO NOT EDIT

sankey <- function(id=NULL, flows=NULL) {
    
    props <- list(id=id, flows=flows)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'Sankey',
        namespace = 'sankey',
        propNames = c('id', 'flows'),
        package = 'sankey'
        )

    structure(component, class = c('dash_component', 'list'))
}
