import { useEffect, useState } from 'react'
import './App.css'
import { default as axios } from 'axios'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import 'bootstrap/dist/css/bootstrap.min.css';
import { Col, Container, Form, Row } from 'react-bootstrap'
import buildUrl from 'build-url-ts';

const url = "http://127.0.0.1:8000"
let chart = <></>

function App() {

  type OptionsType = {
    category: string;
    start_date: string;
    end_date: string;
    smoothing: string;
    avg_days: number;
  };
  const [options, setOptions] = useState<OptionsType>({
    "category": "",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "smoothing": "smoothed",
    "avg_days": 7
  })
  const onFormChange = (e : React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.currentTarget
    console.log(name, value)
    setOptions({...options, [name]: value})
  }

  const [data, setData] = useState(null);

  const [categories, setCategories] = useState([]);



  useEffect(() => {
    const categories_url = buildUrl(url, {
      path: "categories"
    })
    axios.get(categories_url).then(response => {
      let categories = response.data
      categories.unshift("") // inserts at the start of the array
      setCategories(categories)
    })
  })

  useEffect(() => {
    let queryParams = {}
    if (options.category) queryParams = {...queryParams, category: options.category}
    if (options.start_date) queryParams = {...queryParams, start_date: options.start_date} 
    if (options.end_date) queryParams = {...queryParams, end_date: options.end_date}
    if (options.smoothing) queryParams = {...queryParams, smoothing: options.smoothing}
    if (options.avg_days) queryParams = {...queryParams, avg_days: options.avg_days}
    const query_url = buildUrl(url, {
      path: "transactions",
      queryParams: queryParams
    })
    axios.get(query_url).then(response => {
      setData(response.data)
    })
  }, [options])

  if (data != null) {
    chart = (
      <ResponsiveContainer>
        <AreaChart data={data}>
          <Area dataKey="amount"></Area>
          <XAxis dataKey="date"></XAxis>
          <YAxis></YAxis>
          <Tooltip></Tooltip>
        </AreaChart>
      </ResponsiveContainer>
    )
  }

  return (
    <>
      <h1>MoneyViz</h1>
      <Container fluid>
        <Row>
          <Col md={9}>
            {chart}
          </Col>
          <Col md={3}>
            <Form>
              <Form.Group controlId="formCategory">
                <Form.Label>
                  Category
                </Form.Label>
                <Form.Select name="category" value={options.category} onChange={onFormChange}>
                  {categories.map(c => <option value={c}>{c}</option>)}
                </Form.Select>
              </Form.Group>

              <Form.Group controlId="formDate">
                <Form.Label>
                  Start Date
                </Form.Label>
                <Form.Control name="start_date" type="date" value={options.start_date} onChange={onFormChange}></Form.Control>

                <Form.Label>
                  End Date
                </Form.Label>
                <Form.Control name="end_date" type="date" value={options.end_date} onChange={onFormChange}></Form.Control>
              </Form.Group>

              <Form.Group controlId="formSmoothing">
                <Form.Label>
                  Smoothing
                </Form.Label>
                <Form.Select name="smoothing" value={options.smoothing} onChange={onFormChange}>
                  <option value="">None</option>
                  <option value="averaged">Averaged</option>
                  <option value="smoothed">Smoothed</option>
                </Form.Select>

                <Form.Label>
                  Smoothing Radius: {options.avg_days}
                </Form.Label>
                <Form.Range min={1} max={28} name="avg_days" value={options.avg_days} onChange={onFormChange}>

                </Form.Range>
              </Form.Group>
            </Form>
          </Col>
        </Row>
      </Container>

    </>
  )
}

export default App
