import React from "react";
import { useNavigate } from "react-router-dom";
import { Draft } from "../../casualcms/domain/model";
import { AppContext } from "../../config";
import { DeletePopoverForm } from "../layout/confirm";
import { useAuth } from "../login/hooks";

type PageDeletePopoverFormProps = {
  curPage: Draft;
};

export const PageDeletePopoverForm: React.FunctionComponent<
  PageDeletePopoverFormProps
> = (props: PageDeletePopoverFormProps) => {
  const navigate = useNavigate();
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const curPage = props.curPage;

  const [confirmed, setConfirmed] = React.useState<boolean>(false);

  const onSubmit = async () => {
    await config.api.page.deleteDraft(token, curPage.metadata.path);
    setConfirmed(true);
  };

  React.useEffect(() => {
    if (confirmed) {
      const bcItems = curPage.metadata.breadcrumb.items;
      const nextPath =
        bcItems.length >= 2 ? bcItems[bcItems.length - 2].path : "";
      const qs = nextPath
        ? new URLSearchParams({
            parent: nextPath,
          })
        : "";
      navigate(`/admin/pages?${qs}`);
    }
  }, [confirmed]);

  return (
    <DeletePopoverForm button_label="Delete this page" onSubmit={onSubmit} />
  );
};
