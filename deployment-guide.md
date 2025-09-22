# Guía de Despliegue - Serverless AWS Academy

## Prerrequisitos

1. **AWS Academy Learner Lab** activo
2. **AWS CLI** configurado con credenciales de AWS Academy
3. **Terraform** instalado (versión >= 1.0)
4. **Python 3.9+** instalado

## Paso 1: Configurar Credenciales AWS

```bash
# Obtener credenciales desde AWS Academy Learner Lab
# Copiar las credenciales de AWS Details > AWS CLI
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_SESSION_TOKEN="your-session-token"
export AWS_DEFAULT_REGION="us-east-1"
```

## Paso 2: Preparar el Entorno

```bash
# Crear directorio de trabajo
mkdir serverless-aws-academy
cd serverless-aws-academy

# Crear estructura de directorios
mkdir -p lambda/orders_crud lambda/pdf_generator terraform
```

## Paso 3: Configurar Terraform

```bash
# Navegar al directorio terraform
cd terraform

# Inicializar Terraform
terraform init

# Validar configuración
terraform validate

# Revisar plan de ejecución
terraform plan -var="aws_region=us-east-1"
```

## Paso 4: Preparar Código Lambda

```bash
# Crear archivo de función Lambda para CRUD
# El código ya está preparado en lambda/orders_crud/lambda_function.py
# El código ya está preparado en lambda/pdf_generator/lambda_function.py

# Los archivos ZIP se generan automáticamente por Terraform
```

## Paso 5: Desplegar Infraestructura

```bash
# Aplicar configuración Terraform
terraform apply -var="aws_region=us-east-1"

# Confirmar cuando se solicite escribiendo "yes"
```

## Paso 6: Configurar Notificaciones

```bash
# Actualizar suscripción SNS con tu email
terraform apply -var="aws_region=us-east-1" -var="notification_email=tu-email@ejemplo.com"
```

## Paso 7: Verificar Despliegue

```bash
# Obtener outputs de Terraform
terraform output

# Ejemplo de outputs:
# api_gateway_url = "https://abc123.execute-api.us-east-1.amazonaws.com/dev"
# dynamodb_table_name = "serverless-orders-orders"
# s3_bucket_name = "serverless-orders-invoices-a1b2c3d4"
```

## Paso 8: Probar la API

```bash
# Crear una orden (POST)
curl -X POST "https://YOUR_API_URL/dev/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customerName": "Juan Pérez",
    "customerEmail": "juan@example.com",
    "items": ["Laptop", "Mouse"],
    "amount": 299.99
  }'

# Listar órdenes (GET)
curl -X GET "https://YOUR_API_URL/dev/orders"

# Generar PDF (GET)
curl -X GET "https://YOUR_API_URL/dev/orders/ORDER_ID/pdf"
```

## Paso 9: Monitorear

1. **CloudWatch Dashboard**: 
   - Ir a CloudWatch > Dashboards
   - Buscar "serverless-orders-dashboard"

2. **Métricas importantes**:
   - Lambda invocations y errores
   - DynamoDB RCU/WCU consumption
   - API Gateway latencia y errores

3. **Alarmas configuradas**:
   - API Gateway 5XX errors
   - Lambda throttles y errores
   - DynamoDB throttles

## Paso 10: Optimizaciones

### Habilitar Provisioned Concurrency (Horas Pico)
```bash
# Se configura automáticamente via EventBridge
# Horario: 9 AM - 5 PM, Lunes a Viernes
```

### S3 Intelligent Tiering
```bash
# Ya configurado automáticamente para optimizar costos
```

### API Gateway Caching
```bash
# Cache habilitado con TTL de 5 minutos
# Para invalidar cache manualmente:
aws apigateway flush-stage-cache \
  --rest-api-id YOUR_API_ID \
  --stage-name dev
```

## Limpieza de Recursos

```bash
# Destruir toda la infraestructura
terraform destroy -var="aws_region=us-east-1"

# Confirmar cuando se solicite escribiendo "yes"
```

## Solución de Problemas

### Error: "Insufficient permissions"
- Verificar que las credenciales AWS Academy estén activas
- Reiniciar Learner Lab si es necesario

### Error: "Bucket already exists"
- El sufijo random debería evitar esto
- Si persiste, cambiar `bucket_suffix` en variables

### Lambda timeout
- Funciones configuradas con 30s (CRUD) y 60s (PDF)
- Aumentar si es necesario en `lambda.tf`

### DynamoDB throttling
- Configurado en ON_DEMAND mode
- Auto-scaling automático

## Archivos de Configuración

### terraform.tfvars (opcional)
```hcl
aws_region = "us-east-1"
environment = "dev"
project_name = "serverless-orders"
```

### Estructura Final
```
serverless-aws-academy/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── dynamodb.tf
│   ├── s3.tf
│   ├── lambda.tf
│   ├── api_gateway.tf
│   ├── cloudwatch.tf
│   └── lambda_source.tf
├── lambda/
│   ├── orders_crud/
│   │   └── lambda_function.py
│   └── pdf_generator/
│       └── lambda_function.py
└── deployment-guide.md
```

## Métricas de Éxito

- ✅ API Gateway desplegado y funcional
- ✅ Lambda functions ejecutándose
- ✅ DynamoDB con Point-in-Time Recovery
- ✅ S3 con Intelligent Tiering
- ✅ CloudWatch alarmas configuradas
- ✅ Provisioned Concurrency en horas pico
- ✅ Dashboard de monitoreo activo

## Costos Estimados (AWS Academy)

- DynamoDB: On-Demand, solo pagas por uso
- Lambda: Tier gratuito 1M invocaciones/mes
- S3: Tier gratuito 5GB/mes
- API Gateway: Tier gratuito 1M requests/mes
- CloudWatch: Tier gratuito métricas básicas

**Costo estimado mensual**: $0-5 USD en desarrollo normal