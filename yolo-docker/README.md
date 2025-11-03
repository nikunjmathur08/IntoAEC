# IntoAEC YOLO-Only Docker Deployment

This is a streamlined Docker setup for deploying only the YOLO model from the IntoAEC project. Perfect for cloud deployment with minimal dependencies.

## 🚀 Quick Start

### Local Development

1. **Build the Docker image:**
   ```bash
   cd yolo-docker
   docker build -t intoaec-yolo .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 intoaec-yolo
   ```

3. **Or use Docker Compose:**
   ```bash
   docker-compose up --build
   ```

### Cloud Deployment

#### AWS ECS/Fargate
```bash
# Build and tag for ECR
docker build -t intoaec-yolo .
docker tag intoaec-yolo:latest <account>.dkr.ecr.<region>.amazonaws.com/intaec-yolo:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/intaec-yolo:latest
```

#### Google Cloud Run
```bash
# Build and push to GCR
docker build -t gcr.io/<project-id>/intaec-yolo .
docker push gcr.io/<project-id>/intaec-yolo

# Deploy to Cloud Run
gcloud run deploy intoaec-yolo \
  --image gcr.io/<project-id>/intaec-yolo \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2
```

#### Azure Container Instances
```bash
# Build and push to ACR
docker build -t <registry>.azurecr.io/intaec-yolo .
docker push <registry>.azurecr.io/intaec-yolo

# Deploy to ACI
az container create \
  --resource-group <resource-group> \
  --name intoaec-yolo \
  --image <registry>.azurecr.io/intaec-yolo \
  --ports 8000 \
  --memory 2 \
  --cpu 2
```

## 📋 API Endpoints

### Health Check
- **GET** `/` - Basic health check
- **GET** `/health` - Container health check (for orchestration)

### Model Information
- **GET** `/model/info` - Get model details and available classes

### Analysis
- **POST** `/analyze` - Single image analysis
  - Query params: `confidence` (default: 0.25), `iou_threshold` (default: 0.45)
- **POST** `/analyze/batch` - Batch image analysis (max 10 images)

## 🔧 Configuration

### Environment Variables
- `PYTHONUNBUFFERED=1` - Ensures Python output is sent straight to terminal

### Model Path
- Model is located at `/app/model/best2.pt` inside the container
- Make sure your trained YOLO model is copied to the `model/` directory

### Resource Requirements
- **Memory**: 2GB recommended (1GB minimum)
- **CPU**: 2 cores recommended (1 core minimum)
- **Storage**: ~500MB for the container

## 📊 Performance Optimization

### For Production
1. **Use GPU-enabled base image** for better performance:
   ```dockerfile
   FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
   ```

2. **Enable model caching** by pre-loading the model in the container

3. **Use a reverse proxy** (nginx) for load balancing

### Scaling
- **Horizontal**: Deploy multiple container instances
- **Vertical**: Increase memory/CPU allocation
- **Load Balancer**: Use AWS ALB, GCP Load Balancer, or Azure Load Balancer

## 🐛 Troubleshooting

### Common Issues

1. **Model not found error**
   - Ensure `best2.pt` is in the `model/` directory
   - Check file permissions

2. **Out of memory errors**
   - Increase container memory allocation
   - Use CPU-only PyTorch for smaller memory footprint

3. **Slow inference**
   - Use GPU-enabled containers
   - Optimize image preprocessing
   - Consider model quantization

### Logs
```bash
# View container logs
docker logs <container-id>

# Follow logs in real-time
docker logs -f <container-id>
```

## 🔒 Security Considerations

1. **Network Security**
   - Use HTTPS in production
   - Implement authentication if needed
   - Configure firewall rules

2. **Container Security**
   - Use non-root user in production
   - Scan images for vulnerabilities
   - Keep base images updated

3. **Data Privacy**
   - Images are processed in memory
   - Temporary files are cleaned up
   - No persistent storage of uploaded images

## 📈 Monitoring

### Health Checks
- Container health check endpoint: `/health`
- Model loading status included in response

### Metrics to Monitor
- Request latency
- Memory usage
- CPU utilization
- Error rates
- Model inference time

## 🚀 Production Deployment Checklist

- [ ] Model file (`best2.pt`) included in container
- [ ] Health checks configured
- [ ] Resource limits set appropriately
- [ ] Logging configured
- [ ] Monitoring setup
- [ ] Security measures implemented
- [ ] Load balancer configured
- [ ] SSL/TLS certificates installed
- [ ] Backup strategy in place

## 📞 Support

For issues specific to this YOLO-only deployment:
1. Check container logs
2. Verify model file integrity
3. Test with sample images
4. Review resource allocation

For IntoAEC project issues, refer to the main project documentation.
