# 🚀 EmailScope Render Deployment Guide

## Quick Fix for Current Issues

### 1. **Replace your current files with these optimized versions:**

#### **requirements.txt** → **requirements_render.txt**
```bash
# Use the new requirements file with explicit versions
cp requirements_render.txt requirements.txt
```

#### **Add Procfile** (for Render)
```
web: python render_config.py
```

#### **Use render_config.py** as your main launcher
```bash
# Instead of launch_emailscope.py, use:
python render_config.py
```

### 2. **Render Service Configuration**

In your Render dashboard, set these environment variables:

```bash
# Required
PORT=10000  # Render will set this automatically

# Optional (for debugging)
RENDER=true
DEBUG=false
```

### 3. **Build Command**
```bash
pip install -r requirements.txt
```

### 4. **Start Command**
```bash
python render_config.py
```

## 🔧 **What These Changes Fix**

### **Issue 1: Request Timeouts**
- **Problem:** 10-second timeout too short for cloud
- **Fix:** Increased to 30 seconds
- **Impact:** More reliable scraping

### **Issue 2: Aggressive Crawling**
- **Problem:** Too fast for cloud infrastructure
- **Fix:** Slower rate (2s delay vs 0.5s)
- **Impact:** Respects server limits

### **Issue 3: Network Restrictions**
- **Problem:** Bypassing robots.txt causes blocks
- **Fix:** Respect robots.txt on cloud
- **Impact:** Fewer blocked requests

### **Issue 4: Resource Limits**
- **Problem:** Too many concurrent requests
- **Fix:** Reduced max pages (10 vs 30)
- **Impact:** Stays within Render limits

### **Issue 5: DNS Timeouts**
- **Problem:** 1-second DNS timeout too short
- **Fix:** Increased to 5 seconds
- **Impact:** Better email verification

## 📊 **Performance Comparison**

| Setting | Local | Render Optimized |
|---------|-------|------------------|
| Request Delay | 0.5s | 2.0s |
| Timeout | 10s | 30s |
| Max Pages | 30 | 10 |
| Max Depth | 2 | 1 |
| Rate Limit | 0.8s | 2.0s |
| DNS Timeout | 1s | 5s |

## 🚨 **Common Render Issues & Solutions**

### **Issue: "Scraping fails immediately"**
**Solution:** Check logs for timeout errors, increase delays

### **Issue: "No emails found"**
**Solution:** Check if robots.txt is blocking, try different domains

### **Issue: "Process killed"**
**Solution:** Reduce max_pages and max_depth further

### **Issue: "DNS resolution failed"**
**Solution:** Increase verification_timeout to 10 seconds

## 🔍 **Debugging on Render**

### **Check Logs**
1. Go to Render Dashboard
2. Click on your service
3. Go to "Logs" tab
4. Look for error messages

### **Common Error Messages**
- `TimeoutError` → Increase timeout settings
- `ConnectionError` → Check network restrictions
- `DNSException` → Increase DNS timeout
- `Process killed` → Reduce resource usage

### **Test Domains**
Try these domains that work well on cloud:
- `example.com` (always works)
- `github.com` (reliable)
- `stackoverflow.com` (good for testing)

## 🎯 **Expected Results**

After applying these fixes:
- ✅ Scraping should work on Render
- ✅ Fewer timeout errors
- ✅ More reliable email discovery
- ✅ Better error handling
- ✅ Respectful crawling

## 📝 **Deployment Checklist**

- [ ] Replace `requirements.txt` with `requirements_render.txt`
- [ ] Add `Procfile` to project root
- [ ] Use `render_config.py` as main launcher
- [ ] Set environment variables in Render
- [ ] Deploy and test with `example.com`
- [ ] Check logs for any remaining issues

## 🆘 **If Still Not Working**

1. **Check Render logs** for specific error messages
2. **Try with `example.com`** first (most reliable)
3. **Reduce settings further** if needed:
   - `max_pages: 5`
   - `delay: 5.0`
   - `timeout: 60`
4. **Contact support** with specific error messages

---

**Note:** These settings prioritize reliability over speed for cloud deployment. Local development can still use the faster settings.
