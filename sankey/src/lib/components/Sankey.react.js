import React, {PureComponent} from 'react';
import PropTypes from 'prop-types';


export default class SankyArrow extends PureComponent {
  render() {
    const {flows, height: svgHeight, width} = this.props
    if (!flows) {
      return null
    }
    const cumSizes = []
    let cumSize = 0
    flows.forEach(({size}) => {
      cumSizes.push(cumSize)
      cumSize += size
    })
    const topMargin = 30
    const straightHeight = cumSize
    const leftMargin = cumSize
    const rightMargin = 200
    const notchSize = .3
    const lastNotchWidth = notchSize * flows[flows.length - 1].size
    const lastNotchHeight = (.5 + notchSize) * flows[flows.length - 1].size
    const textMarginLeft = 20
    const curve = cumSize
    const totalHeight =
      cumSizes[flows.length - 1] / .414 + topMargin + curve + lastNotchHeight + straightHeight
    const height = svgHeight || totalHeight
    const translateX = flows[flows.length - 1].size * notchSize
    return <svg
      width={width || (leftMargin + cumSize + lastNotchWidth + rightMargin)}
      height={height}>
      <g transform={`translate(${translateX}, ${height - totalHeight})`}>
        {flows.map(({fill, size}, index) => {
          if (index === flows.length - 1) {
            return <path
              key={index}
              d={`M ${cumSize - cumSizes[index]} ${height} h -${size}
              v -${straightHeight + cumSizes[index] / .414 + curve}

              h -${size * notchSize}
              l ${size * (.5 + notchSize)} -${size * (.5 + notchSize)}
              l ${size * (.5 + notchSize)} ${size * (.5 + notchSize)}
              h -${size * notchSize}

              Z`} fill={fill} />
          }
          return <path
            key={index}
            d={`M ${cumSize - cumSizes[index]} ${height} h -${size}
            v -${straightHeight + cumSizes[index] / .414}
            a ${curve} ${curve} 0 0 1 ${curve} -${curve}

            v -${size * notchSize}
            l ${size * (.5 + notchSize)} ${size * (.5 + notchSize)}
            l -${size * (.5 + notchSize)} ${size * (.5 + notchSize)}
            v -${size * notchSize}

            a ${curve - size} ${curve - size} 0 0 0 -${curve - size} ${curve - size}
            Z`} fill={fill} />
        })}
        {flows.map(({size, text}, index) => {
          if (!text) {
            return null
          }
          const isLast = index === flows.length - 1
          const x = isLast ? size * .5 : (cumSize - cumSizes[index] + curve + size * (notchSize - .5))
          const y = height - straightHeight - cumSizes[index] / .414 - curve +
            size * (isLast ? -(.5 + notchSize) : .5)
          const style = {
            dominantBaseline: 'central',
            transform: `translate(${x}px, ${y}px)
              translate${isLast ? 'Y' : 'X'}(${(isLast ? -1 : 1) * textMarginLeft}px)`,
          }
          return <text key={`text-${index}`} style={style}>{text}</text>
        })}
      </g>
    </svg>
  }
}


SankyArrow.defaultProps = {};

SankyArrow.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,

    /**
     * A list of flows to display as arrows.
     */
    flows: PropTypes.arrayOf(PropTypes.shape({
      fill: PropTypes.string,
      size: PropTypes.number.isRequired,
      text: PropTypes.string,
    }).isRequired),

    /**
     * Height of the graph. If not set, it depends on the sum of the sizes of the flows.
     */
    height: PropTypes.number,

    /**
     * Dash-assigned callback that should be called to report property changes
     * to Dash, to make them available for callbacks.
     */
    setProps: PropTypes.func,

    /**
     * Width of the graph. If not set, it depends on the sum of the sizes of the flows.
     */
    width: PropTypes.number,
};
