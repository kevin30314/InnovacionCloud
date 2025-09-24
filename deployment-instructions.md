# Instrucciones Completas de Despliegue - Serverless AWS Academy

## 📋 Prerrequisitos

### 1. Herramientas Requeridas
```bash
# Verificar instalaciones
aws --version          # AWS CLI v2.x
terraform --version    # Terraform >= 1.0
python --version       # Python 3.9+
node --version         # Node.js 18+
npm --version          # npm 8+
```

### 2. Cuentas y Accesos
- ✅ AWS Academy Learner Lab activo
- ✅ Cuenta GitHub para repositorio
- ✅ Email para notificaciones SNS

## 🔧 Configuración Inicial

### Paso 1: Configurar AWS CLI
```bash
# Obtener credenciales desde AWS Academy Learner Lab
# AWS Details > AWS CLI > Show

# Configurar credenciales (válidas por 4 horas)
export AWS_ACCESS_KEY_ID="ASIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
export AWS_DEFAULT_REGION="us-east-1"

# Verificar configuración
aws sts get-caller-identity
```

### Paso 2: Clonar y Configurar Proyecto
```bash
# Clonar repositorio
git clone <repository-url>
cd serverless-inteligente

# Instalar dependencias Python
pip install -r requirements.txt

# Instalar dependencias Node.js
npm install

# Verificar estructura
tree -L 3
```

## 🏗️ Despliegue de Infraestructura

### Paso 3: Preparar Terraform
```bash
# Navegar a directorio terraform
cd terraform

# Inicializar Terraform
terraform init

# Validar configuración
terraform validate

# Formatear archivos
terraform fmt -recursive

# Revisar plan de ejecución
terraform plan -var="aws_region=us-east-1"
```

### Paso 4: Personalizar Variables
```bash
# Crear archivo de variables (opcional)
cat > terraform.tfvars << EOF
aws_region = "us-east-1"
environment = "dev"
project_name = "serverless-orders"
api_stage_name = "dev"
lambda_runtime = "python3.9"
EOF
```

### Paso 5: Desplegar Infraestructura
```bash
# Aplicar configuración
terraform apply -var="aws_region=us-east-1"

# Confirmar escribiendo "yes" cuando se solicite

# Guardar outputs importantes
terraform output > ../terraform-outputs.txt
```

## 🧪 Ejecutar Pruebas

### Paso 6: Pruebas Unitarias
```bash
# Volver al directorio raíz
cd ..

# Ejecutar pruebas unitarias
python -m pytest tests/unit/ -v

# Ejecutar con cobertura
python -m pytest tests/unit/ --cov=lambda --cov-report=html --cov-report=term

# Ver reporte de cobertura
open htmlcov/index.html  # macOS
# o
xdg-open htmlcov/index.html  # Linux
```

### Paso 7: Pruebas de Integración
```bash
# Configurar URL de API desde terraform output
export API_GATEWAY_URL=$(cd terraform && terraform output -raw api_gateway_url)

# Ejecutar pruebas de integración
python -m pytest tests/integration/ -v

# Ejecutar pruebas end-to-end
python -m pytest tests/e2e/ -v
```

## 🔍 Verificación del Despliegue

### Paso 8: Verificar Servicios AWS

#### API Gateway
```bash
# Obtener URL de API
API_URL=$(cd terraform && terraform output -raw api_gateway_url)
echo "API URL: $API_URL"

# Probar endpoint (sin autenticación para prueba inicial)
curl -X GET "$API_URL/orders" \
  -H "Content-Type: application/json"
```

#### Lambda Functions
```bash
# Listar funciones Lambda
aws lambda list-functions --query 'Functions[?contains(FunctionName, `serverless-orders`)].FunctionName'

# Probar función directamente
aws lambda invoke \
  --function-name serverless-orders-orders-crud \
  --payload '{"httpMethod":"GET","pathParameters":{},"queryStringParameters":{}}' \
  response.json

cat response.json
```

#### DynamoDB
```bash
# Verificar tabla
aws dynamodb describe-table --table-name serverless-orders-orders

# Listar elementos (debería estar vacía inicialmente)
aws dynamodb scan --table-name serverless-orders-orders --max-items 5
```

#### S3
```bash
# Listar buckets del proyecto
aws s3 ls | grep serverless-orders

# Verificar configuración del bucket
BUCKET_NAME=$(cd terraform && terraform output -raw s3_bucket_name)
aws s3api get-bucket-location --bucket $BUCKET_NAME
```

### Paso 9: Probar Flujo Completo

#### Crear Orden
```bash
# Crear orden de prueba
curl -X POST "$API_URL/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customerName": "Usuario Prueba",
    "customerEmail": "prueba@example.com",
    "items": ["Producto 1", "Producto 2"],
    "amount": 199.99
  }'
```

#### Listar Órdenes
```bash
# Listar todas las órdenes
curl -X GET "$API_URL/orders"

# Filtrar por estado
curl -X GET "$API_URL/orders?status=pending&limit=10"
```

#### Generar PDF
```bash
# Usar ORDER_ID de la orden creada anteriormente
ORDER_ID="ORD-XXXXXXXX"

curl -X GET "$API_URL/orders/$ORDER_ID/pdf"
```

## 📊 Configurar Monitoreo

### Paso 10: Verificar CloudWatch

#### Dashboard
```bash
# Obtener URL del dashboard
DASHBOARD_URL=$(cd terraform && terraform output -raw cloudwatch_dashboard_url)
echo "Dashboard URL: $DASHBOARD_URL"
```

#### Alarmas
```bash
# Listar alarmas configuradas
aws cloudwatch describe-alarms --alarm-names \
  "serverless-orders-api-gateway-5xx-errors" \
  "serverless-orders-lambda-errors" \
  "serverless-orders-lambda-throttles" \
  "serverless-orders-dynamodb-read-throttled" \
  "serverless-orders-dynamodb-write-throttled"
```

#### Logs
```bash
# Ver logs de Lambda
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/serverless-orders"

# Ver logs recientes
aws logs tail /aws/lambda/serverless-orders-orders-crud --follow
```

### Paso 11: Configurar Notificaciones SNS
```bash
# Obtener ARN del topic
SNS_TOPIC_ARN=$(cd terraform && terraform output -raw sns_topic_arn)

# Suscribirse con email personal
aws sns subscribe \
  --topic-arn $SNS_TOPIC_ARN \
  --protocol email \
  --notification-endpoint tu-email@ejemplo.com

# Confirmar suscripción desde el email recibido
```

## 🔐 Configurar Autenticación (Opcional)

### Paso 12: Cognito User Pool
```bash
# Crear usuario de prueba
USER_POOL_ID=$(aws cognito-idp list-user-pools --max-results 10 --query 'UserPools[?Name==`serverless-orders-user-pool`].Id' --output text)

aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username testuser \
  --user-attributes Name=email,Value=test@example.com \
  --temporary-password TempPass123! \
  --message-action SUPPRESS
```

## 🚀 Despliegue del Frontend

### Paso 13: Build y Deploy Frontend
```bash
# Build del frontend
npm run build

# Subir a S3 (si tienes bucket de hosting estático)
# aws s3 sync dist/ s3://your-frontend-bucket --delete

# O ejecutar localmente
npm run dev
```

## 📈 Optimizaciones de Producción

### Paso 14: Habilitar Optimizaciones

#### Provisioned Concurrency (Horas Pico)
```bash
# Verificar configuración de EventBridge
aws events list-rules --name-prefix "serverless-orders"

# Verificar Provisioned Concurrency
aws lambda get-provisioned-concurrency-config \
  --function-name serverless-orders-orders-crud \
  --qualifier '$LATEST'
```

#### S3 Intelligent Tiering
```bash
# Verificar configuración
aws s3api get-bucket-intelligent-tiering-configuration \
  --bucket $BUCKET_NAME \
  --id EntireBucket
```

#### API Gateway Caching
```bash
# Verificar configuración de cache
aws apigateway get-stage \
  --rest-api-id $(aws apigateway get-rest-apis --query 'items[?name==`serverless-orders-api`].id' --output text) \
  --stage-name dev
```

## 🧹 Limpieza y Mantenimiento

### Paso 15: Scripts de Mantenimiento

#### Limpiar Logs Antiguos
```bash
# Script para limpiar logs de CloudWatch
cat > cleanup-logs.sh << 'EOF'
#!/bin/bash
LOG_GROUPS=$(aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/serverless-orders" --query 'logGroups[].logGroupName' --output text)

for LOG_GROUP in $LOG_GROUPS; do
  echo "Cleaning up $LOG_GROUP"
  aws logs put-retention-policy --log-group-name $LOG_GROUP --retention-in-days 7
done
EOF

chmod +x cleanup-logs.sh
./cleanup-logs.sh
```

#### Backup de DynamoDB
```bash
# Habilitar backup automático
aws dynamodb put-backup-policy \
  --table-name serverless-orders-orders \
  --backup-policy BackupEnabled=true
```

### Paso 16: Destruir Infraestructura (Cuando sea necesario)
```bash
# CUIDADO: Esto eliminará toda la infraestructura
cd terraform

# Revisar qué se va a eliminar
terraform plan -destroy

# Confirmar y destruir
terraform destroy -auto-approve

# Limpiar archivos locales
rm -rf .terraform/
rm terraform.tfstate*
```

## 📋 Checklist de Verificación

### ✅ Infraestructura
- [ ] Terraform apply exitoso
- [ ] Todas las funciones Lambda desplegadas
- [ ] DynamoDB table creada con GSI
- [ ] S3 buckets configurados
- [ ] API Gateway endpoints funcionando
- [ ] CloudWatch dashboard visible
- [ ] SNS topic y suscripciones activas

### ✅ Funcionalidad
- [ ] CRUD de órdenes funcionando
- [ ] Generación de PDF exitosa
- [ ] Filtros de búsqueda operativos
- [ ] Notificaciones SNS enviándose
- [ ] Logs apareciendo en CloudWatch

### ✅ Pruebas
- [ ] Tests unitarios pasando (≥8 tests)
- [ ] Cobertura de código ≥80%
- [ ] Tests de integración exitosos
- [ ] Tests E2E completados

### ✅ Monitoreo
- [ ] Alarmas configuradas y activas
- [ ] Dashboard mostrando métricas
- [ ] Logs estructurados visibles
- [ ] Notificaciones por email funcionando

### ✅ Optimización
- [ ] Provisioned Concurrency programada
- [ ] S3 Intelligent Tiering activo
- [ ] API Gateway caching habilitado
- [ ] Costos monitoreados

## 🆘 Solución de Problemas

### Error: "Insufficient permissions"
```bash
# Verificar credenciales
aws sts get-caller-identity

# Renovar credenciales desde AWS Academy
# AWS Details > AWS CLI > Show (copiar nuevas credenciales)
```

### Error: "Resource already exists"
```bash
# Limpiar estado de Terraform
terraform refresh

# O importar recurso existente
terraform import aws_s3_bucket.example bucket-name
```

### Lambda timeout
```bash
# Aumentar timeout en terraform/lambda.tf
resource "aws_lambda_function" "orders_crud" {
  timeout = 60  # Aumentar de 30 a 60 segundos
}

# Aplicar cambios
terraform apply
```

### DynamoDB throttling
```bash
# Verificar métricas
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=serverless-orders-orders \
  --start-time 2025-01-18T00:00:00Z \
  --end-time 2025-01-18T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

## 📞 Soporte

### Recursos de Ayuda
- **AWS Documentation**: https://docs.aws.amazon.com/
- **Terraform AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/
- **AWS Academy Support**: Foros de AWS Academy
- **Stack Overflow**: Tags `aws-lambda`, `terraform`, `dynamodb`

### Logs Importantes
```bash
# Logs de Terraform
terraform show

# Logs de Lambda
aws logs tail /aws/lambda/serverless-orders-orders-crud

# Logs de API Gateway
aws logs tail /aws/apigateway/serverless-orders-api
```

---

**¡Despliegue completado exitosamente!** 🎉

Tu aplicación serverless está ahora funcionando en AWS con todas las optimizaciones y monitoreo configurados.