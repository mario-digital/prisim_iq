# 5. API Specification

## 5.1 REST API (OpenAPI 3.1)

```yaml
openapi: 3.1.0
info:
  title: PrismIQ Dynamic Pricing API
  version: 1.0.0
  description: |
    Agentic, chat-driven dynamic pricing copilot API.
    Provides price optimization, explainability, and scenario analysis endpoints.

servers:
  - url: http://localhost:8000
    description: Local development server
  - url: http://localhost:8000/api/v1
    description: Versioned API path

tags:
  - name: Health
    description: System health and status
  - name: Data
    description: Dataset exploration
  - name: Chat
    description: Conversational interface
  - name: Pricing
    description: Price optimization
  - name: Scenarios
    description: Scenario management

paths:
  /health:
    get:
      tags: [Health]
      summary: Health check
      operationId: getHealth
      responses:
        '200':
          description: Service healthy
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'

  /api/v1/data/summary:
    get:
      tags: [Data]
      summary: Get dataset summary statistics
      operationId: getDataSummary
      responses:
        '200':
          description: Dataset summary
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DataSummary'

  /api/v1/data/segment/{segment_id}:
    get:
      tags: [Data]
      summary: Get segment details
      operationId: getSegmentDetails
      parameters:
        - name: segment_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Segment details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SegmentDetails'

  /api/v1/chat:
    post:
      tags: [Chat]
      summary: Send chat message
      operationId: sendChatMessage
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ChatRequest'
      responses:
        '200':
          description: Chat response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatResponse'

  /api/v1/chat/stream:
    post:
      tags: [Chat]
      summary: Stream chat response
      operationId: streamChatMessage
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ChatRequest'
      responses:
        '200':
          description: SSE stream
          content:
            text/event-stream:
              schema:
                type: string

  /api/v1/optimize_price:
    post:
      tags: [Pricing]
      summary: Optimize price for market context
      operationId: optimizePrice
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PricingRequest'
      responses:
        '200':
          description: Pricing result
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PricingResult'

  /api/v1/scenarios:
    get:
      tags: [Scenarios]
      summary: List saved scenarios
      operationId: listScenarios
      responses:
        '200':
          description: Scenario list
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Scenario'
    post:
      tags: [Scenarios]
      summary: Create scenario
      operationId: createScenario
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateScenarioRequest'
      responses:
        '201':
          description: Created scenario
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Scenario'

  /api/v1/scenarios/{scenario_id}:
    get:
      tags: [Scenarios]
      summary: Get scenario by ID
      operationId: getScenario
      parameters:
        - name: scenario_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Scenario details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Scenario'
    delete:
      tags: [Scenarios]
      summary: Delete scenario
      operationId: deleteScenario
      parameters:
        - name: scenario_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: Deleted

  /api/v1/scenarios/compare:
    post:
      tags: [Scenarios]
      summary: Compare scenarios
      operationId: compareScenarios
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CompareRequest'
      responses:
        '200':
          description: Comparison results
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ScenarioComparison'

components:
  schemas:
    HealthResponse:
      type: object
      properties:
        status:
          type: string
          enum: [healthy, degraded, unhealthy]
        version:
          type: string
        timestamp:
          type: string
          format: date-time
        checks:
          type: object
          additionalProperties:
            type: boolean

    ChatRequest:
      type: object
      required: [message]
      properties:
        message:
          type: string
        conversationId:
          type: string
        context:
          $ref: '#/components/schemas/MarketContext'

    ChatResponse:
      type: object
      properties:
        id:
          type: string
        role:
          type: string
          enum: [assistant]
        content:
          type: string
        toolResults:
          type: array
          items:
            $ref: '#/components/schemas/ToolResult'
        visualizations:
          type: array
          items:
            type: string
        pricing:
          $ref: '#/components/schemas/PricingResult'

    PricingRequest:
      type: object
      required: [context]
      properties:
        context:
          $ref: '#/components/schemas/MarketContext'

    # Additional schemas match TypeScript interfaces above
    MarketContext:
      type: object
      properties:
        location:
          type: string
          enum: [Urban, Suburban, Rural]
        timestamp:
          type: string
          format: date-time
        timeOfDay:
          type: string
          enum: [Morning, Afternoon, Evening, Night]
        riders:
          type: integer
          minimum: 10
          maximum: 100
        drivers:
          type: integer
          minimum: 5
          maximum: 80
        supplyDemandRatio:
          type: number
        customerSegment:
          type: string
        loyaltyTier:
          type: string
          enum: [Bronze, Silver, Gold, Platinum]
        vehicleType:
          type: string
          enum: [Economy, Premium]

    PricingResult:
      type: object
      properties:
        recommendedPrice:
          type: number
        basePrice:
          type: number
        multiplier:
          type: number
        confidence:
          type: number
        explanation:
          $ref: '#/components/schemas/PriceExplanation'

    PriceExplanation:
      type: object
      properties:
        narrative:
          type: string
        topFactors:
          type: array
          items:
            $ref: '#/components/schemas/FeatureContribution'

    FeatureContribution:
      type: object
      properties:
        feature:
          type: string
        value:
          oneOf:
            - type: string
            - type: number
        impact:
          type: number
        direction:
          type: string
          enum: [positive, negative]

    ToolResult:
      type: object
      properties:
        toolName:
          type: string
        success:
          type: boolean
        result:
          type: object
        executionTimeMs:
          type: number

    Scenario:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        context:
          $ref: '#/components/schemas/MarketContext'
        result:
          $ref: '#/components/schemas/PricingResult'

    DataSummary:
      type: object
      properties:
        totalRecords:
          type: integer
        segments:
          type: array
          items:
            type: string
        priceRange:
          type: object
          properties:
            min:
              type: number
            max:
              type: number
            mean:
              type: number

    SegmentDetails:
      type: object
      properties:
        segmentId:
          type: string
        recordCount:
          type: integer
        avgPrice:
          type: number
        characteristics:
          type: object

    CreateScenarioRequest:
      type: object
      required: [name, context]
      properties:
        name:
          type: string
        description:
          type: string
        context:
          $ref: '#/components/schemas/MarketContext'

    CompareRequest:
      type: object
      required: [scenarioIds]
      properties:
        scenarioIds:
          type: array
          items:
            type: string
          minItems: 2
          maxItems: 5

    ScenarioComparison:
      type: object
      properties:
        scenarios:
          type: array
          items:
            $ref: '#/components/schemas/Scenario'
        insights:
          type: array
          items:
            type: string
```

---
