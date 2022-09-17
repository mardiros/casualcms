import React from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { Page } from "../../casualcms/domain/model";
import { AppContext } from "../../config";
import { DeletePopoverForm } from "../layout/confirm";
import { useAuth } from "../login/hooks";

type PageDeletePopoverFormProps = {
  curPage: Page;
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
    await config.api.page.deletePage(token, curPage.meta.path);
    setConfirmed(true);
  };

  React.useEffect(() => {
    if (confirmed) {
      const nextPath =
      curPage.meta.breadcrumb.length >= 2
        ? curPage.meta.breadcrumb[curPage.meta.breadcrumb.length - 2].path
        : "";
      const qs = nextPath
        ? new URLSearchParams({
            parent: nextPath,
          })
        : "";
      navigate(`/admin/pages?${qs}`)
    }
  }, [confirmed]);

  return (
    <DeletePopoverForm button_label="Delete this page" onSubmit={onSubmit} />
  );
};
