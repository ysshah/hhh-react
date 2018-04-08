import React, { Component } from 'react'
// import Range from 'rc-slider/lib/Range'
// import 'rc-slider/assets/index.css'
import moment from 'moment'

const Date = ({date, onClick}) => (
  <div>
    <button onClick={() => onClick(date.clone().subtract(1, 'days'))}>v</button>
    {date.format('L')}
    <button onClick={() => onClick(date.clone().add(1, 'days'))}>^</button>
  </div>
)

const DateRange = ({start, end, change}) => (
  <div className='d-flex'>
    <Date date={start} onClick={date => change('start', date)}/>
    <div className='mx-3'>to</div>
    <Date date={end} onClick={date => change('end', date)}/>
  </div>
)

class App extends Component {
  constructor(props) {
    super(props)
    this.change = this.change.bind(this)
    const end = moment()
    const start = end.clone().subtract(1, 'days')
    this.state = {posts: [], start, end}
  }

  componentDidMount() {
    const { start, end } = this.state
    this.getPosts(start, end)
  }

  componentDidUpdate(prevProps, prevState) {
    const { start, end } = this.state
    if (prevState.start !== start || prevState.end !== end) {
      this.getPosts(start, end)
    }
  }

  getPosts(start, end) {
    fetch(`/posts/${start.unix()}/${end.unix()}`)
      .then(r => r.json())
      .then(posts => this.setState({posts}))
  }

  change(k, v) {
    this.setState({[k]: v})
  }

  render() {
    const { start, end, posts } = this.state
    return (
      <div className='container mt-4'>
        <div className="row justify-content-center">
          <div className="col-8">
            {start && end && <DateRange start={start} end={end} change={this.change} />}
            {posts.map(p => <div>{p.score} - {p.title} - {moment.unix(p.create_time).format('L LT')}</div>)}
          </div>
        </div>
      </div>
    );
  }
}

export default App;
