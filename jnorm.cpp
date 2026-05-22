// jnorm.cpp  –  interval Jacobian ∞-norm for LLVM bit-code
// g++ -O2 jnorm.cpp $(llvm-config-15 --cxxflags --ldflags --libs core irreader) -o jnorm
// ./jnorm target.bc func_name

#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>
#include <llvm/IRReader/IRReader.h>
#include <llvm/Support/SourceMgr.h>
#include <llvm/Support/CommandLine.h>
#include <iostream>
#include <memory>
#include <vector>
#include <cmath>
#include <algorithm>

using namespace llvm;

// tiny interval class
struct I { double l, u; };
inline I operator+(I a, I b) { return {a.l + b.l, a.u + b.u}; }
inline I operator-(I a, I b) { return {a.l - b.u, a.u - b.l}; }
inline I operator*(I a, I b) {
    double t[4] = {a.l*b.l, a.l*b.u, a.u*b.l, a.u*b.u};
    return { *std::min_element(t,t+4), *std::max_element(t,t+4) };
}

static I visit(Value *v, const std::vector<I> &args);

static I eval(Instruction *inst, const std::vector<I> &args)
{
    switch (inst->getOpcode()) {
    case Instruction::FAdd: return visit(inst->getOperand(0), args) + visit(inst->getOperand(1), args);
    case Instruction::FSub: return visit(inst->getOperand(0), args) - visit(inst->getOperand(1), args);
    case Instruction::FMul: return visit(inst->getOperand(0), args) * visit(inst->getOperand(1), args);
    default: return { -INFINITY, INFINITY };  // unsupported → worst case
    }
}

static I visit(Value *v, const std::vector<I> &args)
{
    if (Argument *a = dyn_cast<Argument>(v)) return args[a->getArgNo()];
    if (ConstantFP *c = dyn_cast<ConstantFP>(v)) return { c->getValueAPF().convertToDouble(), c->getValueAPF().convertToDouble() };
    if (Instruction *i = dyn_cast<Instruction>(v)) return eval(i, args);
    return { -INFINITY, INFINITY };
}

int main(int argc, char *argv[])
{
    if (argc != 3) { std::cerr << "usage: jnorm file.bc func_name\n"; return 1; }

    LLVMContext ctx;
    SMDiagnostic err;
    std::unique_ptr<Module> M = parseIRFile(argv[1], err, ctx);
    if (!M) { std::cerr << "parseIRFile failed\n"; return 2; }

    Function *F = M->getFunction(argv[2]);
    if (!F) { std::cerr << "function not found\n"; return 1; }

    const size_t n = F->arg_size();
    std::vector<I> args(n, { -1.0, 1.0 });  // input interval [-1,1]

    // compute ∞-norm of Jacobian row-wise
    double norm = 0.0;
    for (BasicBlock &BB : *F)
        for (Instruction &I : BB)
            if (isa<Instruction>(&I) && I.getType()->isDoubleTy()) {
                struct I row = visit(&I, args);
                double m = std::max(std::fabs(row.l), std::fabs(row.u));
                if (m > norm) norm = m;
            }

    std::cout << norm << '\n';
    return (norm < 1.0) ? 0 : 1;
}
