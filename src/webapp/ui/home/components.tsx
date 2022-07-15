import React from "react";
import {
  Box,
  Heading,
} from "@chakra-ui/react";
import { PartialPage } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";

import { useAuth } from "../login/components";
import { Link, Navigate } from "react-router-dom";
import { Result } from "neverthrow";
import { Loader } from "../loader/components";

export const HomePage: React.FunctionComponent<{}> = () => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const [pages, setPages] = React.useState<PartialPage[]>([]);
  const [error, setError] = React.useState<ApiError>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);

  React.useEffect(() => {
    async function loadPages() {
      let pages: Result<PartialPage[], ApiError>;
      pages = await config.api.page.listPages(token, null);
      pages
        .map((pages: PartialPage[]) => setPages(pages))
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    loadPages();
    return function cleanup() {};
  }, []);

  if (isLoading) {
    return <Loader label="preparing data..." />;
  }

  if (!error && pages.length) {
    return <Navigate to="/admin/pages" replace />;
  }
  return (
    <>
      <Heading>Welcome {auth.authenticatedUser?.username}!</Heading>
      <Box>
        <Link to="/admin/page/new">Create my first page</Link>.
      </Box>
    </>
  );
};
