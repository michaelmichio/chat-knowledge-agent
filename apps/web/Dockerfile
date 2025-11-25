# ---------------------------
# 1. Builder Stage
# ---------------------------
FROM node:20-alpine AS builder

# Workdir
WORKDIR /app

# Copy only package files first (improves caching)
COPY package*.json ./

# Install dependencies for build
RUN npm install

# Copy all project files
COPY . .

# Build Next.js (generate .next)
RUN npm run build


# ---------------------------
# 2. Runner Stage (Production)
# ---------------------------
FROM node:20-alpine AS runner

WORKDIR /app

# Install only production dependencies
COPY package*.json ./
RUN npm install --omit=dev

# Copy needed files from builder (not entire folder)
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

# If you use Next.js app dir: copy .next/standalone as well
# Uncomment if needed
# COPY --from=builder /app/.next/standalone ./

# Expose port
EXPOSE 3000

# Ensure PORT is set
ENV PORT=3000

# Start production server
CMD ["npm", "start"]
