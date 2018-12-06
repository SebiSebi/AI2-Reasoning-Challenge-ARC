package clients;

import static io.grpc.MethodDescriptor.generateFullMethodName;
import static io.grpc.stub.ClientCalls.asyncBidiStreamingCall;
import static io.grpc.stub.ClientCalls.asyncClientStreamingCall;
import static io.grpc.stub.ClientCalls.asyncServerStreamingCall;
import static io.grpc.stub.ClientCalls.asyncUnaryCall;
import static io.grpc.stub.ClientCalls.blockingServerStreamingCall;
import static io.grpc.stub.ClientCalls.blockingUnaryCall;
import static io.grpc.stub.ClientCalls.futureUnaryCall;
import static io.grpc.stub.ServerCalls.asyncBidiStreamingCall;
import static io.grpc.stub.ServerCalls.asyncClientStreamingCall;
import static io.grpc.stub.ServerCalls.asyncServerStreamingCall;
import static io.grpc.stub.ServerCalls.asyncUnaryCall;
import static io.grpc.stub.ServerCalls.asyncUnimplementedStreamingCall;
import static io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall;

/**
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.11.0)",
    comments = "Source: answer_service.proto")
public final class AnswerServiceGrpc {

  private AnswerServiceGrpc() {}

  public static final String SERVICE_NAME = "services.AnswerService";

  // Static method descriptors that strictly reflect the proto.
  @io.grpc.ExperimentalApi("https://github.com/grpc/grpc-java/issues/1901")
  @java.lang.Deprecated // Use {@link #getAnswerMethod()} instead. 
  public static final io.grpc.MethodDescriptor<clients.AnswerServiceProtos.AnswerRequest,
      clients.AnswerServiceProtos.AnswerResponse> METHOD_ANSWER = getAnswerMethodHelper();

  private static volatile io.grpc.MethodDescriptor<clients.AnswerServiceProtos.AnswerRequest,
      clients.AnswerServiceProtos.AnswerResponse> getAnswerMethod;

  @io.grpc.ExperimentalApi("https://github.com/grpc/grpc-java/issues/1901")
  public static io.grpc.MethodDescriptor<clients.AnswerServiceProtos.AnswerRequest,
      clients.AnswerServiceProtos.AnswerResponse> getAnswerMethod() {
    return getAnswerMethodHelper();
  }

  private static io.grpc.MethodDescriptor<clients.AnswerServiceProtos.AnswerRequest,
      clients.AnswerServiceProtos.AnswerResponse> getAnswerMethodHelper() {
    io.grpc.MethodDescriptor<clients.AnswerServiceProtos.AnswerRequest, clients.AnswerServiceProtos.AnswerResponse> getAnswerMethod;
    if ((getAnswerMethod = AnswerServiceGrpc.getAnswerMethod) == null) {
      synchronized (AnswerServiceGrpc.class) {
        if ((getAnswerMethod = AnswerServiceGrpc.getAnswerMethod) == null) {
          AnswerServiceGrpc.getAnswerMethod = getAnswerMethod = 
              io.grpc.MethodDescriptor.<clients.AnswerServiceProtos.AnswerRequest, clients.AnswerServiceProtos.AnswerResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(
                  "services.AnswerService", "Answer"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  clients.AnswerServiceProtos.AnswerRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  clients.AnswerServiceProtos.AnswerResponse.getDefaultInstance()))
                  .setSchemaDescriptor(new AnswerServiceMethodDescriptorSupplier("Answer"))
                  .build();
          }
        }
     }
     return getAnswerMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static AnswerServiceStub newStub(io.grpc.Channel channel) {
    return new AnswerServiceStub(channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static AnswerServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    return new AnswerServiceBlockingStub(channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static AnswerServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    return new AnswerServiceFutureStub(channel);
  }

  /**
   */
  public static abstract class AnswerServiceImplBase implements io.grpc.BindableService {

    /**
     */
    public void answer(clients.AnswerServiceProtos.AnswerRequest request,
        io.grpc.stub.StreamObserver<clients.AnswerServiceProtos.AnswerResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getAnswerMethodHelper(), responseObserver);
    }

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return io.grpc.ServerServiceDefinition.builder(getServiceDescriptor())
          .addMethod(
            getAnswerMethodHelper(),
            asyncUnaryCall(
              new MethodHandlers<
                clients.AnswerServiceProtos.AnswerRequest,
                clients.AnswerServiceProtos.AnswerResponse>(
                  this, METHODID_ANSWER)))
          .build();
    }
  }

  /**
   */
  public static final class AnswerServiceStub extends io.grpc.stub.AbstractStub<AnswerServiceStub> {
    private AnswerServiceStub(io.grpc.Channel channel) {
      super(channel);
    }

    private AnswerServiceStub(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected AnswerServiceStub build(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      return new AnswerServiceStub(channel, callOptions);
    }

    /**
     */
    public void answer(clients.AnswerServiceProtos.AnswerRequest request,
        io.grpc.stub.StreamObserver<clients.AnswerServiceProtos.AnswerResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getAnswerMethodHelper(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   */
  public static final class AnswerServiceBlockingStub extends io.grpc.stub.AbstractStub<AnswerServiceBlockingStub> {
    private AnswerServiceBlockingStub(io.grpc.Channel channel) {
      super(channel);
    }

    private AnswerServiceBlockingStub(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected AnswerServiceBlockingStub build(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      return new AnswerServiceBlockingStub(channel, callOptions);
    }

    /**
     */
    public clients.AnswerServiceProtos.AnswerResponse answer(clients.AnswerServiceProtos.AnswerRequest request) {
      return blockingUnaryCall(
          getChannel(), getAnswerMethodHelper(), getCallOptions(), request);
    }
  }

  /**
   */
  public static final class AnswerServiceFutureStub extends io.grpc.stub.AbstractStub<AnswerServiceFutureStub> {
    private AnswerServiceFutureStub(io.grpc.Channel channel) {
      super(channel);
    }

    private AnswerServiceFutureStub(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected AnswerServiceFutureStub build(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      return new AnswerServiceFutureStub(channel, callOptions);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<clients.AnswerServiceProtos.AnswerResponse> answer(
        clients.AnswerServiceProtos.AnswerRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getAnswerMethodHelper(), getCallOptions()), request);
    }
  }

  private static final int METHODID_ANSWER = 0;

  private static final class MethodHandlers<Req, Resp> implements
      io.grpc.stub.ServerCalls.UnaryMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ServerStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ClientStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.BidiStreamingMethod<Req, Resp> {
    private final AnswerServiceImplBase serviceImpl;
    private final int methodId;

    MethodHandlers(AnswerServiceImplBase serviceImpl, int methodId) {
      this.serviceImpl = serviceImpl;
      this.methodId = methodId;
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public void invoke(Req request, io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        case METHODID_ANSWER:
          serviceImpl.answer((clients.AnswerServiceProtos.AnswerRequest) request,
              (io.grpc.stub.StreamObserver<clients.AnswerServiceProtos.AnswerResponse>) responseObserver);
          break;
        default:
          throw new AssertionError();
      }
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public io.grpc.stub.StreamObserver<Req> invoke(
        io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        default:
          throw new AssertionError();
      }
    }
  }

  private static abstract class AnswerServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    AnswerServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return clients.AnswerServiceProtos.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("AnswerService");
    }
  }

  private static final class AnswerServiceFileDescriptorSupplier
      extends AnswerServiceBaseDescriptorSupplier {
    AnswerServiceFileDescriptorSupplier() {}
  }

  private static final class AnswerServiceMethodDescriptorSupplier
      extends AnswerServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final String methodName;

    AnswerServiceMethodDescriptorSupplier(String methodName) {
      this.methodName = methodName;
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.MethodDescriptor getMethodDescriptor() {
      return getServiceDescriptor().findMethodByName(methodName);
    }
  }

  private static volatile io.grpc.ServiceDescriptor serviceDescriptor;

  public static io.grpc.ServiceDescriptor getServiceDescriptor() {
    io.grpc.ServiceDescriptor result = serviceDescriptor;
    if (result == null) {
      synchronized (AnswerServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new AnswerServiceFileDescriptorSupplier())
              .addMethod(getAnswerMethodHelper())
              .build();
        }
      }
    }
    return result;
  }
}
