# ---------- Build stage ----------
FROM node:20-alpine AS builder
WORKDIR /app
# package.json is in the project root, so we copy from the build context (root)
COPY package*.json ./
RUN npm ci
# Copy the whole repo (we only use the frontend bits at build)
COPY . .
RUN npm run build

# ---------- Runtime stage ----------
FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app ./
EXPOSE 3000
CMD ["npm", "run", "start"]
