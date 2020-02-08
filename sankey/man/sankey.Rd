% Auto-generated: do not edit by hand
\name{sankey}

\alias{sankey}

\title{Sankey component}

\description{

}

\usage{
sankey(id=NULL, flows=NULL, height=NULL, width=NULL)
}

\arguments{
\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{flows}{List of lists containing elements 'fill', 'size', 'text'.
those elements have the following types:
  - fill (character; optional)
  - size (numeric; required)
  - text (character; optional)s. A list of flows to display as arrows.}

\item{height}{Height of the graph. If not set, it depends on the sum of the sizes of the flows.}

\item{width}{Width of the graph. If not set, it depends on the sum of the sizes of the flows.}
}
