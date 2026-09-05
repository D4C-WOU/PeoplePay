"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ListOrdered, Plus } from "lucide-react";

import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { LoadingBanner, ErrorBanner } from "@/components/shared/state-banner";
import { EmptyState } from "@/components/shared/empty-state";
import {
  useSalaryRules,
  useSalaryStructures,
  salaryRuleApi,
} from "@/hooks/usePayroll";
import { ApiError } from "@/lib/api";
import type { CalculationType, SalaryRuleCategory } from "@/types/payroll";

function NewRuleDialog({
  structureId,
  onCreated,
}: {
  structureId: string;
  onCreated: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [category, setCategory] = useState<SalaryRuleCategory>("EARNING");
  const [calcType, setCalcType] = useState<CalculationType>("FIXED");
  const [amount, setAmount] = useState("");
  const [percentage, setPercentage] = useState("");
  const [formula, setFormula] = useState("");
  const [sequence, setSequence] = useState("10");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await salaryRuleApi.create({
        salary_structure_id: structureId,
        code,
        name,
        category,
        calculation_type: calcType,
        amount: calcType === "FIXED" ? Number(amount) : undefined,
        percentage: calcType === "PERCENTAGE" ? Number(percentage) : undefined,
        formula: calcType === "FORMULA" ? formula : undefined,
        sequence: Number(sequence),
        is_active: true,
      });
      setOpen(false);
      setCode("");
      setName("");
      setAmount("");
      setPercentage("");
      setFormula("");
      onCreated();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not create rule.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button disabled={!structureId} />}>
        <Plus /> New rule
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New salary rule</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="code">Code</Label>
              <Input
                id="code"
                value={code}
                onChange={(e) => setCode(e.target.value.toUpperCase())}
                required
                placeholder="BASIC"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="sequence">Sequence</Label>
              <Input
                id="sequence"
                type="number"
                min={1}
                value={sequence}
                onChange={(e) => setSequence(e.target.value)}
                required
              />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="Basic Salary"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Category</Label>
              <Select
                value={category}
                onValueChange={(v) => setCategory(v as SalaryRuleCategory)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="EARNING">Earning</SelectItem>
                  <SelectItem value="DEDUCTION">Deduction</SelectItem>
                  <SelectItem value="TAX">Tax</SelectItem>
                  <SelectItem value="EMPLOYER_CONTRIBUTION">
                    Employer contribution
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Calculation</Label>
              <Select
                value={calcType}
                onValueChange={(v) => setCalcType(v as CalculationType)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="FIXED">Fixed amount</SelectItem>
                  <SelectItem value="PERCENTAGE">
                    Percentage of gross
                  </SelectItem>
                  <SelectItem value="FORMULA">Formula</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {calcType === "FIXED" && (
            <div className="space-y-1.5">
              <Label htmlFor="amount">Amount</Label>
              <Input
                id="amount"
                type="number"
                step="0.01"
                min={0}
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
              />
            </div>
          )}
          {calcType === "PERCENTAGE" && (
            <div className="space-y-1.5">
              <Label htmlFor="percentage">Percentage (%)</Label>
              <Input
                id="percentage"
                type="number"
                step="0.01"
                min={0}
                value={percentage}
                onChange={(e) => setPercentage(e.target.value)}
                required
              />
            </div>
          )}
          {calcType === "FORMULA" && (
            <div className="space-y-1.5">
              <Label htmlFor="formula">Formula</Label>
              <Textarea
                id="formula"
                value={formula}
                onChange={(e) => setFormula(e.target.value)}
                placeholder="gross * 0.12"
                required
              />
              <p className="text-xs text-muted-foreground">
                Available variables: base_salary, gross, total_earnings,
                total_deductions, total_tax, worked_days, overtime_hours
              </p>
            </div>
          )}

          {error && (
            <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {error}
            </p>
          )}
          <DialogFooter>
            <DialogClose render={<Button variant="outline" type="button" />}>
              Cancel
            </DialogClose>
            <Button type="submit" disabled={saving}>
              {saving ? "Saving…" : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function SalaryRulesContent() {
  const searchParams = useSearchParams();
  const initialStructureId = searchParams.get("structure_id") ?? "";
  const [structureId, setStructureId] = useState(initialStructureId);

  const { data: structures } = useSalaryStructures();
  const {
    data: rules,
    loading,
    error,
    reload,
  } = useSalaryRules(structureId || undefined);

  return (
    <div className="flex flex-1 flex-col">
      <Header
        title="Salary Rules"
        description="Rules execute in sequence to compute gross, deductions, and net pay."
        actions={<NewRuleDialog structureId={structureId} onCreated={reload} />}
      />
      <div className="flex-1 space-y-4 p-4 sm:p-6">
        <Select value={structureId} onValueChange={setStructureId}>
          <SelectTrigger className="w-64">
            <SelectValue placeholder="Select a salary structure" />
          </SelectTrigger>
          <SelectContent>
            {structures?.map((s) => (
              <SelectItem key={s.id} value={s.id}>
                {s.name} ({s.code})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {error && <ErrorBanner message={error} />}
        {!structureId ? (
          <EmptyState
            icon={ListOrdered}
            title="Select a salary structure"
            description="Choose a structure above to view or add its salary rules."
          />
        ) : loading ? (
          <LoadingBanner label="Loading salary rules…" />
        ) : !rules || rules.length === 0 ? (
          <EmptyState
            icon={ListOrdered}
            title="No salary rules yet"
            description="Add rules — this structure will not compute payslips without them."
          />
        ) : (
          <div className="overflow-hidden rounded-xl border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Seq</TableHead>
                  <TableHead>Code</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Calculation</TableHead>
                  <TableHead>Value</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rules
                  .slice()
                  .sort((a, b) => a.sequence - b.sequence)
                  .map((rule) => (
                    <TableRow key={rule.id}>
                      <TableCell>{rule.sequence}</TableCell>
                      <TableCell className="font-mono text-xs">
                        {rule.code}
                      </TableCell>
                      <TableCell className="font-medium">{rule.name}</TableCell>
                      <TableCell className="capitalize text-muted-foreground">
                        {rule.category.replaceAll("_", " ").toLowerCase()}
                      </TableCell>
                      <TableCell className="capitalize text-muted-foreground">
                        {rule.calculation_type.toLowerCase()}
                      </TableCell>
                      <TableCell>
                        {rule.calculation_type === "FIXED" && rule.amount}
                        {rule.calculation_type === "PERCENTAGE" &&
                          `${rule.percentage}%`}
                        {rule.calculation_type === "FORMULA" && (
                          <code className="text-xs">{rule.formula}</code>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={rule.is_active ? "default" : "secondary"}
                        >
                          {rule.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </div>
  );
}

export default function SalaryRulesPage() {
  return (
    <Suspense
      fallback={
        <div className="p-4 sm:p-6">
          <LoadingBanner label="Loading salary rules…" />
        </div>
      }
    >
      <SalaryRulesContent />
    </Suspense>
  );
}
