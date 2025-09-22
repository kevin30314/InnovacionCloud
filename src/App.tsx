import React, { useState } from 'react';
import { 
  Cloud, 
  Database, 
  FileText, 
  BarChart3, 
  Settings, 
  Plus,
  Search,
  Filter,
  Download,
  Eye,
  Trash2,
  Edit,
  CheckCircle,
  AlertCircle,
  TrendingUp
} from 'lucide-react';

interface Order {
  orderId: string;
  createdAt: string;
  customerName: string;
  amount: number;
  status: 'pending' | 'completed' | 'cancelled';
  items: string[];
}

interface Metric {
  label: string;
  value: string;
  change: string;
  trend: 'up' | 'down' | 'neutral';
}

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  // Mock data
  const orders: Order[] = [
    {
      orderId: 'ORD-001',
      createdAt: '2025-01-18T10:30:00Z',
      customerName: 'Juan Pérez',
      amount: 299.99,
      status: 'completed',
      items: ['Laptop', 'Mouse']
    },
    {
      orderId: 'ORD-002',
      createdAt: '2025-01-18T11:15:00Z',
      customerName: 'María García',
      amount: 149.50,
      status: 'pending',
      items: ['Smartphone Case']
    },
    {
      orderId: 'ORD-003',
      createdAt: '2025-01-18T12:00:00Z',
      customerName: 'Carlos López',
      amount: 89.99,
      status: 'cancelled',
      items: ['Headphones']
    }
  ];

  const metrics: Metric[] = [
    { label: 'Total Orders', value: '1,234', change: '+12.5%', trend: 'up' },
    { label: 'Revenue', value: '$45,678', change: '+8.3%', trend: 'up' },
    { label: 'DynamoDB RCU', value: '156', change: '-5.2%', trend: 'down' },
    { label: 'Lambda Invocations', value: '2,890', change: '+15.7%', trend: 'up' }
  ];

  const filteredOrders = orders.filter(order => {
    const matchesSearch = order.customerName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         order.orderId.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || order.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-50';
      case 'pending': return 'text-orange-600 bg-orange-50';
      case 'cancelled': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getTrendIcon = (trend: string) => {
    return trend === 'up' ? (
      <TrendingUp className="w-4 h-4 text-green-500" />
    ) : (
      <TrendingUp className="w-4 h-4 text-red-500 rotate-180" />
    );
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard Serverless</h1>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>AWS Services Active</span>
          </div>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <div key={index} className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-all duration-200 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">{metric.label}</p>
                <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
              </div>
              <div className="text-right">
                {getTrendIcon(metric.trend)}
                <p className={`text-sm font-medium ${metric.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                  {metric.change}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Architecture Overview */}
      <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Arquitectura Serverless</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-6">
          {[
            { icon: Cloud, label: 'API Gateway', color: 'bg-blue-500' },
            { icon: Database, label: 'Lambda Functions', color: 'bg-orange-500' },
            { icon: Database, label: 'DynamoDB', color: 'bg-purple-500' },
            { icon: FileText, label: 'S3 Storage', color: 'bg-green-500' },
            { icon: BarChart3, label: 'CloudWatch', color: 'bg-red-500' },
            { icon: Settings, label: 'CloudFront', color: 'bg-indigo-500' }
          ].map((service, index) => (
            <div key={index} className="text-center group">
              <div className={`${service.color} p-4 rounded-xl mx-auto w-16 h-16 flex items-center justify-center group-hover:scale-110 transition-transform duration-200`}>
                <service.icon className="w-8 h-8 text-white" />
              </div>
              <p className="text-sm text-gray-600 mt-3 font-medium">{service.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Orders Preview */}
      <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Órdenes Recientes</h2>
          <button 
            onClick={() => setActiveTab('orders')}
            className="text-blue-600 hover:text-blue-700 font-medium text-sm"
          >
            Ver todas →
          </button>
        </div>
        <div className="space-y-3">
          {orders.slice(0, 3).map((order) => (
            <div key={order.orderId} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div>
                  <p className="font-medium text-gray-900">{order.orderId}</p>
                  <p className="text-sm text-gray-600">{order.customerName}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-medium text-gray-900">${order.amount}</p>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(order.status)}`}>
                  {order.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderOrders = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Gestión de Órdenes</h1>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium flex items-center space-x-2 transition-colors duration-200">
          <Plus className="w-4 h-4" />
          <span>Nueva Orden</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0 md:space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por cliente o ID de orden..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">Todos los estados</option>
                <option value="pending">Pendiente</option>
                <option value="completed">Completado</option>
                <option value="cancelled">Cancelado</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Orders Table */}
      <div className="bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">ID Orden</th>
                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Cliente</th>
                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Monto</th>
                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Estado</th>
                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Fecha</th>
                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredOrders.map((order) => (
                <tr key={order.orderId} className="hover:bg-gray-50 transition-colors duration-150">
                  <td className="py-4 px-6">
                    <span className="font-mono text-sm text-gray-900">{order.orderId}</span>
                  </td>
                  <td className="py-4 px-6">
                    <span className="font-medium text-gray-900">{order.customerName}</span>
                  </td>
                  <td className="py-4 px-6">
                    <span className="font-semibold text-gray-900">${order.amount}</span>
                  </td>
                  <td className="py-4 px-6">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>
                      {order.status === 'completed' && <CheckCircle className="w-3 h-3 inline mr-1" />}
                      {order.status === 'pending' && <AlertCircle className="w-3 h-3 inline mr-1" />}
                      {order.status}
                    </span>
                  </td>
                  <td className="py-4 px-6">
                    <span className="text-sm text-gray-600">
                      {new Date(order.createdAt).toLocaleDateString()}
                    </span>
                  </td>
                  <td className="py-4 px-6">
                    <div className="flex items-center space-x-2">
                      <button className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors duration-150">
                        <Eye className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors duration-150">
                        <Download className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-gray-600 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-colors duration-150">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-150">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderInfrastructure = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Infraestructura AWS</h1>
        <div className="flex items-center space-x-2 text-sm text-green-600">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span>Terraform Ready</span>
        </div>
      </div>

      {/* Infrastructure Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          { service: 'API Gateway', status: 'Active', endpoints: 8, color: 'green' },
          { service: 'Lambda Functions', status: 'Active', endpoints: 12, color: 'green' },
          { service: 'DynamoDB', status: 'Active', endpoints: 2, color: 'green' },
          { service: 'S3 Buckets', status: 'Active', endpoints: 3, color: 'green' },
          { service: 'CloudWatch', status: 'Monitoring', endpoints: 15, color: 'blue' },
          { service: 'IAM Roles', status: 'Configured', endpoints: 6, color: 'purple' }
        ].map((item, index) => (
          <div key={index} className="bg-white p-6 rounded-xl shadow-md border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">{item.service}</h3>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                item.color === 'green' ? 'bg-green-50 text-green-700' :
                item.color === 'blue' ? 'bg-blue-50 text-blue-700' :
                'bg-purple-50 text-purple-700'
              }`}>
                {item.status}
              </span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{item.endpoints}</p>
            <p className="text-sm text-gray-600">Resources</p>
          </div>
        ))}
      </div>

      {/* Terraform Code Preview */}
      <div className="bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden">
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Configuración Terraform</h2>
        </div>
        <div className="p-6">
          <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
            <pre className="text-green-400 text-sm">
{`# DynamoDB Table Configuration
resource "aws_dynamodb_table" "orders" {
  name           = "orders"
  billing_mode   = "ON_DEMAND"
  hash_key       = "orderId"
  range_key      = "createdAt"
  
  point_in_time_recovery {
    enabled = true
  }
}

# S3 Bucket for PDF Invoices
resource "aws_s3_bucket" "invoices" {
  bucket = "serverless-invoices-\${random_id.bucket_suffix.hex}"
}

# API Gateway
resource "aws_api_gateway_rest_api" "orders_api" {
  name        = "orders-api"
  description = "Serverless Orders API"
}`}
            </pre>
          </div>
        </div>
      </div>

      {/* Deployment Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">Instrucciones de Despliegue</h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p>• Configura AWS CLI con credenciales de AWS Academy</p>
          <p>• Ejecuta <code className="bg-blue-100 px-2 py-1 rounded">terraform init</code></p>
          <p>• Planifica con <code className="bg-blue-100 px-2 py-1 rounded">terraform plan</code></p>
          <p>• Despliega con <code className="bg-blue-100 px-2 py-1 rounded">terraform apply</code></p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Cloud className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">Serverless AWS Academy</h1>
            </div>
            <nav className="flex space-x-1">
              {[
                { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
                { id: 'orders', label: 'Órdenes', icon: FileText },
                { id: 'infrastructure', label: 'Infraestructura', icon: Settings }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
                    activeTab === tab.id
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'orders' && renderOrders()}
        {activeTab === 'infrastructure' && renderInfrastructure()}
      </main>
    </div>
  );
}

export default App;