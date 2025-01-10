import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface MissingTransactionsAlertProps {
  symbols: string[];
  onContinue: () => void;
  onUpload: () => void;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function MissingTransactionsAlert({
  symbols,
  onContinue,
  onUpload,
  open,
  onOpenChange,
}: MissingTransactionsAlertProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>⚠️ Önemli Vergi Uyarısı</AlertDialogTitle>
          <AlertDialogDescription className="space-y-4">
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
              <p className="font-medium text-red-400 mb-2">
                Eksik İşlem Tespit Edildi!
              </p>
              <div className="space-y-2">
                {symbols.map((symbol) => (
                  <div key={symbol} className="flex items-start space-x-2">
                    <span className="text-red-400 mt-1">•</span>
                    <p className="text-gray-300">
                      <span className="font-semibold text-red-400">{symbol}</span> hissesinin alım işlemini bulamadık. Bu durum vergi hesaplamasının hatalı olmasına neden olabilir.
                    </p>
                  </div>
                ))}
              </div>
            </div>
            <p className="text-gray-300">
              Doğru vergi hesaplaması için lütfen daha önceki tarihlerdeki ekstrelerinizi de yükleyin.
            </p>
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogAction onClick={onUpload} className="sm:w-full">
            Eski Ekstreleri Yükle
          </AlertDialogAction>
          <AlertDialogCancel onClick={onContinue} className="sm:w-full">
            Vergi Hesaplamaya Devam Et
          </AlertDialogCancel>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
} 